tellme - text-to-speech command execution notifier
=======================================

tellme runs the command and notify the user through text-to-speech when the
process finishes.

For example:

    tellme sudo yum update

will eventually say "finished yum update successfully". Yes, it's smart
enough to strip the sudo out. Some configuration options are available, see
the example configuration file. With that file,

    cd myproject
    tellme make install

will eventually say "finished myproject make install successfully".

Dependencies 
------------

festival is currently hardcoded as the text-to-speech engine.
