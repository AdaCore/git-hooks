#! /usr/bin/env python
"""A dummy cvs_check program that passes all files.

It also prints a trace on stdout, in order to allow us to allow us
to verify that the script was called with the correct arguments.
"""
from __future__ import print_function
import sys

filenames = sys.stdin.read().splitlines(False)

# To help with testing, print a trace containing the name of the module
# and the names of the files being checked.
print("cvs_check: %s < %s" % (
    ' '.join(["`%s'" % arg for arg in sys.argv[1:]]),
    ' '.join(["`%s'" % arg for arg in filenames])))

# We should never be called for file `b', because the user requested
# that this file not have pre-commit checks run on it (via a .gitattribute
# file).  If that's the case, error out.

for filename in filenames:
    if filename.endswith('/b'):
	print("Error: Style violations detected in file: %s" % filename)
	sys.exit(1)
