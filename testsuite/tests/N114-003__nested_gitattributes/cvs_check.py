#! /usr/bin/env python
"""A dummy cvs_check program.
"""
import sys

filename = sys.argv[1]
if filename.endswith('test.py'):
    print "cvs_check: `%s' is violating restriction A.3.1(b)" % filename
    sys.exit(1)

# To help with testing, print a trace containing the name of the file
# that is being checked.
print "cvs_check: `%s'" % filename
