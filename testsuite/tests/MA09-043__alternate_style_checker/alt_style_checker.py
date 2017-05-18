#! /usr/bin/env python
"""A dummy cvs_check program that passes all files.

It also prints a trace on stdout, in order to allow us to allow us
to verify that the script was called with the correct arguments.
"""
import sys

# To help with testing, print a trace containing the name of the file
# that is being checked.
print "alt_style_checker: `%s' `%s'" % (sys.argv[1], sys.argv[2])
