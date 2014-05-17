tellme - command execution notifier
===================================

tellme is used to run commands in the background and notify the user when
the command has finished. It does this through two methods:

* text-to-speech: on completion of the task, tell the user the program
  finished
* log to system: on completion of the task, add a journal log entry


Dependencies 
------------

* festival for text-to-speech
* systemd for systemd-cat
