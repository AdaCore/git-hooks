#! /usr/bin/env python
"""A dummy cvs_check program that FAILs all files.
"""
import sys

# To help with testing, print a trace containing the name of the module
# and the names of the files being checked.
print "cvs_check: %s < %s" % (
    ' '.join(["`%s'" % arg for arg in sys.argv[1:]]),
    ' '.join(["`%s'" % arg for arg in sys.stdin.read().splitlines(False)]))

filenames = sys.stdin.read().splitlines(False)

print >> sys.stderr, \
    'ERROR: %s: Copyright year in header is not up to date' % filenames[0]
sys.exit(1)
