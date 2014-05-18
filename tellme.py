#!/usr/bin/env python

import glob
import re
import sys
import os
import subprocess
import ConfigParser

def usage():
	print "usage: %s command [options]" % os.path.basename(sys.argv[0])

def error(msg):
	print >> sys.stderr, msg
	sys.exit(1)

def talk(command, status):
	p = subprocess.Popen(["festival", "--tts"], stdin=subprocess.PIPE)
	msg = "finished %s" % str(command)
	if status != 0:
		msg += " with error %d" % status
	else:
		msg += " successfully"
	p.communicate(msg)

class Command(object):
	configpath = os.getenv("XDG_CONFIG_HOME",  "%s/.config" % os.environ["HOME"])
	def __init__(self, command):
		self.commandline = self._strip_sudo(command)
		self.binary = os.path.basename(self.commandline[0])
		# default is just to speak the binary
		self.output = self.binary

		self._apply_config()

	def _strip_sudo(self, args):
		if os.path.basename(args[0]) == "sudo":
			args = args[1:]
		return args

	def __str__(self):
		return self.output

	def _apply_config(self):
		self.config = ConfigParser.SafeConfigParser()

		paths = glob.glob("%s/tellme/*.conf" % (self.configpath))

		# run up from cwd to first instance of .tellme existing
		cwd = os.getcwd()
		while not os.path.isdir("%s/.tellme" % cwd):
			cwd = os.path.realpath(cwd + "/..")
			if os.path.dirname(cwd) == cwd:
				break

		paths + glob.glob("%s/.tellme/*.conf" % (cwd))

		if len(self.config.read(paths)) == 0:
			return

		command = self.binary
		if command == "general":
			error("Seriously? A command called general?")

		wl = []
		bl = []
		if self.config.has_option(command, "whitelist"):
			wl = self.config.get(command, "whitelist").split(" ")
		if self.config.has_option(command, "blacklist"):
			bl = self.config.get(command, "blacklist").split(" ")
		argstring = self._filter_args(wl, bl)
		directory = self._get_directory()
		self.output = "%s %s %s" % (directory, command, argstring)

	def _get_directory(self):
		command = self.binary
		want_dir = "none"
		if self.config.has_option("general", "directory"):
			want_dir = self.config.get("general", "directory")

		if self.config.has_option(command, "directory"):
			want_dir = self.config.get(command, "directory")

		if want_dir == "none": 
			return ""
		elif want_dir == "pwd":
			return os.path.basename(os.getcwd())
		elif want_dir == "git":
			path = os.getcwd()
			found = True
			while not os.path.isdir("%s/.git" % path):
				path = os.path.realpath(path + "/..")
				if os.path.dirname(path) == path:
					found = False
					break
			if found:
				path = os.path.basename(path)
			else:
				path = os.path.basename(os.getcwd())

			return path
		return ""

	def _filter_args(self, whitelist, blacklist):
		args = self.commandline[1:]

                # drop all blacklisted args first
		for pat in blacklist:
			if pat == "":
				continue
			pattern = re.compile(pat)
			args = [ a for a in args if not pattern.match(a) ]

		# whitelist only applies if it exists
		if len(whitelist) > 0:
			whitelisted = []
			for arg in args:
				matches = [ x for x in whitelist if re.match(x, arg) ]
				if len(matches) > 0:
					whitelisted.append(arg)
			args = whitelisted

		return " ".join(args)

if __name__ == "__main__":
	if len(sys.argv) == 1:
		usage()
		sys.exit(1)

	command = sys.argv[1:]
	rc = subprocess.call(command, stdin=0, stdout=1, stderr=2)
	cmd = Command(command)
	talk(cmd, rc)
	sys.exit(rc)

