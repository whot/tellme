dist_bin_SCRIPTS = tellme
tellmedir = $(datadir)/tellme/
tellme_DATA = tellme-default.conf

SUFFIXES = .1

SED_SUBS=-e "s|\@datarootdir\@|$(datarootdir)|"

if HAVE_PANDOC
dist_man1_MANS = tellme.1
.man.1:
	sed $(SED_SUBS) $^ | $(PANDOC) -s -t man -o $@
endif

tellme: tellme.py
	sed $(SED_SUBS) $^ > $@

CLEANFILES = $(dist_man1_MANS) $(dist_bin_SCRIPTS)
EXTRA_DIST = tellme.py tellme-default.conf tellme.man
