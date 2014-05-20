AC_PREREQ([2.60])
AC_INIT([text-to-speech command execution notifier],
	[0.1],
	[],
	[tellme])

AM_INIT_AUTOMAKE([foreign dist-xz no-dist-gzip])
AM_SILENT_RULES([yes])

# We don't actually need a compiler, but automake complains about missing AMDEP
AC_PROG_CC
AC_PROG_INSTALL
AM_PATH_PYTHON([2.6])
AC_ARG_VAR([PANDOC], [Path to pandoc command])
AC_PATH_PROG([PANDOC], [pandoc])
if test "x$PANDOC" = "x"; then
	AC_MSG_WARN([pandoc not found - required for man pages])
fi
AM_CONDITIONAL(HAVE_PANDOC, [test "x$PANDOC" != "x"])

AC_PATH_PROG([FESTIVAL], [festival])
if test "x$FESTIVAL" = "x"; then
	AC_MSG_WARN([festival not found on this machine - required for voice output])
fi

AC_CONFIG_FILES([Makefile])
AC_OUTPUT
