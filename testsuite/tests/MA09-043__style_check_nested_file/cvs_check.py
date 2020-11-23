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

# Also, to verify that the file to be checked is accessible from
# the style checker, dump its contents. This also allows to verify
# that it's the right version of the file, btw.
for filename in filenames:
    print("File `%s' contains:" % filename)
    with open(filename, 'r') as fd:
	print(fd.read())
    print("--- Done ---")

# And simulate a rejection.  Passing a relative path of the filename
# is really only useful when the style-check detects some errors.
# So simulate that in this testcase.
sys.exit(1)
