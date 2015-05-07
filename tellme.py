#!/usr/bin/env python

from __future__ import print_function
import errno
import glob
import re
import sys
import os
import subprocess
try:
	import configparser
except ImportError:
	import ConfigParser as configparser

def usage():
	print("usage: %s command [options]" % os.path.basename(sys.argv[0]))

def error(msg):
	print(msg, file=sys.stderr)
	sys.exit(1)

class Command(object):
	sysconfigpath = "@datarootdir@"
	configpath = os.getenv("XDG_CONFIG_HOME",  "%s/.config" % os.environ["HOME"])
	def __init__(self, command, status):
		self.commandline = self._strip_sudo(command)
		self.binary = os.path.basename(self.commandline[0])
		# default is just to speak the binary
		self.output = self.binary
		self.status = status

		self._apply_config()

	def _strip_sudo(self, args):
		if os.path.basename(args[0]) == "sudo":
			args = args[1:]
		return args

	def __str__(self):
		return self.output

	def _get_config_option(self, option):
		val = None
		if self.config.has_option("general", option):
			val = self.config.get("general", option)

		if self.config.has_option(self.binary, option):
			val = self.config.get(self.binary, option)
		return val

	def _apply_config(self):
		self.config = configparser.SafeConfigParser()

		paths = glob.glob("%s/tellme/*.conf" % (self.sysconfigpath))
		paths += glob.glob("%s/tellme/*.conf" % (self.configpath))

		# run up from cwd to first instance of .tellme existing
		cwd = os.getcwd()
		while not os.path.isdir("%s/.tellme" % cwd):
			cwd = os.path.realpath(cwd + "/..")
			if os.path.dirname(cwd) == cwd:
				break

		paths += glob.glob("%s/.tellme/*.conf" % (cwd))

		if len(self.config.read(paths)) == 0:
			return

		command = self.binary
		if command == "general":
			error("Seriously? A command called general?")

		argstring = self._filter_args()
		directory = self._get_directory()
		self.output = "%s %s %s" % (directory, command, argstring)

	def _get_directory(self):
		want_dir = self._get_config_option("directory")

		path = ""
		if want_dir == "none":
			pass
		elif want_dir == "cwd":
			path = os.path.basename(os.getcwd())
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
		return self._sub_directory(path)

	def _sub_directory(self, directory):
		subs = self._get_config_option("dirsubs") or ""
		subs = subs.split(" ")

		for pat in subs:
			if len(pat) == 0:
				continue
			if len(pat) <= 3:
				error("Invalid regex '%s' in dirsubs='%s'", pat, " ".join(subs))
			fields = pat.split(pat[0])
			if len(fields) < 4:
				error("Invalid regex '%s' in dirsubs='%s'", pat, " ".join(subs))
			if re.match(fields[1], directory):
				directory = re.sub(fields[1], fields[2], directory)
				break
		return directory


	def _filter_args(self):
		wl = self._get_config_option("whitelist") or ""
		wl = [x for x in  wl.split(" ") if len(x) > 0]
		bl = self._get_config_option("blacklist") or ""
		bl = [x for x in  bl.split(" ") if len(x) > 0]

		args = self.commandline[1:]
		if len(bl) == 0 and len(wl) == 0:
			args = []

                # drop all blacklisted args first
		for pat in bl:
			if pat == "":
				continue
			pattern = re.compile(pat)
			args = [ a for a in args if not pattern.match(a) ]

		# whitelist only applies if it exists
		if len(wl) > 0:
			whitelisted = []
			for arg in args:
				matches = [ x for x in wl if re.match(x, arg) ]
				if len(matches) > 0:
					whitelisted.append(arg)
			args = whitelisted

		return " ".join(args)

	def talk(self):
		if self.status == 0:
			if self._get_config_option("talk") == "error":
				return

		# voice output can take a while, no need to wait until it finished.
		# call festival from the child process, so we don't hang the
		# terminal
		if os.fork() == 0:
			p = subprocess.Popen(["festival", "--tts"], stdin=subprocess.PIPE)
			msg = "finished %s" % str(self.output)
			if self.status != 0:
				msg += " with error %d" % self.status
			else:
				msg += " successfully"
			p.communicate(msg.encode("utf-8"))
			sys.exit(0)

if __name__ == "__main__":
	if len(sys.argv) == 1:
		usage()
		sys.exit(1)

	try:
		command = sys.argv[1:]
		rc = subprocess.call(command, stdin=0, stdout=1, stderr=2)
		cmd = Command(command, rc)
		cmd.talk()
		sys.exit(rc)
	except OSError as e:
		if e.errno == errno.ENOENT:
			print("command not found: %s" % command[0])
		else:
			print("%s: %s" % (command[0], e.strerror))
		sys.exit(127)

