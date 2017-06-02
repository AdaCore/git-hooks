#! /usr/bin/env python
"""A dummy cvs_check that pretends that certain files fail the style check.

It also prints a trace on stdout, in order to allow us to allow us
to verify that the script was called with the correct arguments.
"""
import sys

filenames = sys.stdin.read().splitlines(False)

# To help with testing, print a trace containing the name of the module
# and the names of the files being checked.
print >> sys.stderr, "cvs_check: %s < %s" % (
    ' '.join(["`%s'" % arg for arg in sys.argv[1:]]),
    ' '.join(["`%s'" % arg for arg in filenames]))

# Fail the style-check for the following files:
for filename in filenames:
    if filename == 'pck.ads':
	print >> sys.stderr, \
	    "ERROR: style-check error detected for file: `%s'." % filename
	print >> sys.stderr, 'ERROR: Copyright year in header is not up to date'
	sys.exit(1)
