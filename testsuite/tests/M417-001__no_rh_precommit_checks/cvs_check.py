#! /usr/bin/env python
"""A dummy cvs_check program that passes all files.

It also prints a trace on stdout, in order to allow us to allow us
to verify that the script was called with the correct arguments.
"""
import sys

if sys.argv[2] == 'b':
    print >>sys.stderr, "cvs_check: style check violation in %s" % sys.argv[2]
    sys.exit(1)
