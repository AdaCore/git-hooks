#! /usr/bin/env python
"""A dummy cvs_check program.
"""
import sys

filenames = sys.stdin.read().splitlines(False)

# To help with testing, print a trace containing the name of the module
# and the names of the files being checked.
print "cvs_check: %s < %s" % (
    ' '.join(["`%s'" % arg for arg in sys.argv[1:]]),
    ' '.join(["`%s'" % arg for arg in filenames]))

for filename in filenames:
    if filename.endswith('test.py'):
        print "cvs_check: `%s' is violating restriction A.3.1(b)" % filename
        sys.exit(1)
