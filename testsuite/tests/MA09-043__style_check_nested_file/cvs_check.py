#! /usr/bin/env python
"""A dummy cvs_check program that passes all files.

It also prints a trace on stdout, in order to allow us to allow us
to verify that the script was called with the correct arguments.
"""
import sys

# To help with testing, print a trace containing the name of the file
# that is being checked. In particular, we want the second argument,
# to verify that it has the relative path (from the project's root
# directory) to the file being style-checked.
print "cvs_check: `%s' `%s'" % (sys.argv[1], sys.argv[2])

# Also, to verify that the file to be checked is accessible from
# the style checker, dump its contents. This also allows to verify
# that it's the right version of the file, btw.
print "File `%s' contains:" % sys.argv[2]
with open(sys.argv[2], 'r') as fd:
    print fd.read()
print "--- Done ---"

# And simulate a rejection.  Passing a relative path of the filename
# is really only useful when the style-check detects some errors.
# So simulate that in this testcase.
sys.exit(1)
