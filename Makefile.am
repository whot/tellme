dist_bin_SCRIPTS = tellme
dist_man1_MANS = tellme.1

SUFFIXES = .1

.man.1:
	$(PANDOC) -s -t man $< -o $@

tellme: tellme.py
	sed -e "s|\@datarootdir\@|$(datarootdir)|" $^ > $@

CLEANFILES = $(dist_man1_MANS) $(dist_bin_SCRIPTS)
EXTRA_DIST = tellme.example.conf
