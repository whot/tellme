dist_bin_SCRIPTS = tellme
dist_man1_MANS = tellme.1

SUFFIXES = .1

SED_SUBS=-e "s|\@datarootdir\@|$(datarootdir)|"

.man.1:
	sed $(SED_SUBS) $^ | $(PANDOC) -s -t man -o $@

tellme: tellme.py
	sed $(SED_SUBS) $^ > $@

CLEANFILES = $(dist_man1_MANS) $(dist_bin_SCRIPTS)
EXTRA_DIST = tellme.example.conf
