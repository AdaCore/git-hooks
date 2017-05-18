#! /usr/bin/env python
"""A dummy cvs_check that pretends that certain files fail the style check.

It also prints a trace on stdout, in order to allow us to allow us
to verify that the script was called with the correct arguments.
"""
import sys

# To help with testing, print a trace containing the name of the module
# and the name of the file being checked.
print >> sys.stderr, "cvs_check: `%s' `%s'" % (sys.argv[1], sys.argv[2])

# Fail the style-check for the following files:
if sys.argv[2] == 'pck.ads':
    print >> sys.stderr, \
        "ERROR: style-check error detected for file: `%s'." % sys.argv[2]
    print >> sys.stderr, 'ERROR: Copyright year in header is not up to date'
    sys.exit(1)
