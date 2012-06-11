#! /usr/bin/env python
"""A dummy cvs_check program that passes all files.

It also prints a trace on stdout, in order to allow us to allow us
to verify that the script was called with the correct arguments.
"""
import sys

filename = sys.argv[1]

# To help with testing, print a trace containing the name of the file
# that is being checked.
print "cvs_check: `%s'" % filename

# We should never be called for file `b', because the user requested
# that this file not have pre-commit checks run on it (via a .gitattribute
# file).  If that's the case, error out.

if filename.endswith('/b'):
    print "Error: Style violations detected in file: %s" % filename
    sys.exit(1)

