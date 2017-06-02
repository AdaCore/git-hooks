#! /usr/bin/env python
"""A dummy cvs_check program that fails all files.
"""
import sys

filenames = sys.stdin.read().splitlines(False)

# To help with testing, print a trace containing the name of the module
# and the names of the files being checked.
print >> sys.stderr, "cvs_check: %s < %s" % (
    ' '.join(["`%s'" % arg for arg in sys.argv[1:]]),
    ' '.join(["`%s'" % arg for arg in filenames]))

print >> sys.stderr, 'ERROR: style-check should not be performed.'
sys.exit(1)
