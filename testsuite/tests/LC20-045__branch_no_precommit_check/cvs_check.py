#! /usr/bin/env python
"""A dummy cvs_check program that fails all files.
"""
import sys

# To help with testing, print a trace containing the name of the file
# that is being checked.
print >> sys.stderr, "cvs_check: `%s' `%s'" % (sys.argv[1], sys.argv[2])

# Fail the style-check for the following files:
print >> sys.stderr, 'ERROR: style-check should not be performed.'
sys.exit(1)
