#! /usr/bin/env python
"""A dummy cvs_check program that passes all files.

It also prints a trace on stdout, in order to allow us to allow us
to verify that the script was called with the correct arguments
for the correct files.
"""
from __future__ import print_function
import sys

# To help with testing, print a trace containing the name of the module
# and the names of the files being checked.
print("cvs_check: %s < %s" % (
    ' '.join(["`%s'" % arg for arg in sys.argv[1:]]),
    ' '.join(["`%s'" % arg for arg in sys.stdin.read().splitlines(False)])))
if len(sys.argv) > 2 and sys.argv[1] in ('--config', '-c'):
    with open(sys.argv[2]) as f:
        print(f.read())
