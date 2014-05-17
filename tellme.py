#!/usr/bin/env python

import re
import sys
import os
import subprocess
import ConfigParser

def usage():
	print "usage: %s command [options]" % os.path.basename(sys.argv[0])

def strip_sudo(args):
	if os.path.basename(args[0]) == "sudo":
		args = args[1:]
	return args

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
		self.commandline = strip_sudo(command)
		self.binary = os.path.basename(self.commandline[0])
		# default is just to speak the binary
		self.output = self.binary

		self._apply_config()

	def __str__(self):
		return self.output

	def _apply_config(self):
		config = ConfigParser.SafeConfigParser()

		paths = ["%s/tellme/%s.conf" % (self.configpath, self.binary)]

		# run up from cwd to first instance of .tellme existing
		cwd = os.getcwd()
		while not os.path.isdir("%s/.tellme" % cwd):
			cwd = os.path.realpath(cwd + "/..")
			if os.path.dirname(cwd) == cwd:
				break

		paths.append("%s/.tellme/%s.conf" % (cwd, self.binary))

		if len(config.read(paths)) == 0:
			return

		arguments = config.get("talk", "arguments")
		if arguments == "all":
			self.output = " ".join(self.commandline)
		elif arguments == "filtered":
			wl = ""
			bl = ""

			if config.has_option("talk", "arguments_whitelist"):
				wl = config.get("talk", "arguments_whitelist")
			if config.has_option("talk", "arguments_blacklist"):
				bl = config.get("talk", "arguments_blacklist")
			self.output = self._filter_output(wl.split(" "), bl.split(" "))


	def _get_directory(self):
		if not config.has_option("talk", "directory"):
			return

		want_dir = config.get("talk", "directory")
		if want_dir == "none": 
			return
		elif want_dir == "pwd":
			self.output = "%s %s" % (os.path.basename(os.getcwd()), self.output)
		elif want_dir == "git":
			path = os.getcwd()
			found = True
			while not os.path.isdir("%s/.git" % path):
				path = os.path.realpath(path + "/..")
				if os.path.dirname(path) == path:
					found = False
					break
			if found:
				self.output = "%s %s" % (os.path.basename(path), self.output)
			else:
				self.output = "%s %s" % (os.path.basename(os.getcwd()), self.output)

	def _filter_output(self, whitelist, blacklist):
		output_args = self.commandline[1:]

		for pat in blacklist:
			if pat == "":
				continue
			pattern = re.compile(pat)
			output_args = [ x for x in output_args if not pattern.match(x) ]

		output = self.binary
		for arg in output_args:
			matches = [ x for x in whitelist if re.match(x, arg) ]
			if len(matches) > 0:
				output += " %s" % arg

		return output

if __name__ == "__main__":
	if len(sys.argv) == 1:
		usage()
		sys.exit(1)

	command = sys.argv[1:]
	rc = subprocess.call(command, stdin=0, stdout=1, stderr=2)
	cmd = Command(command)
	talk(cmd, rc)
	sys.exit(rc)

