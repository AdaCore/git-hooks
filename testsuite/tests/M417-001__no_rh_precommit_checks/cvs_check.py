#! /usr/bin/env python
"""A dummy cvs_check program that passes all files.

It also prints a trace on stdout, in order to allow us to allow us
to verify that the script was called with the correct arguments.
"""
import sys

filenames = sys.stdin.read().splitlines(False)

for filename in filenames:
    if filename == "b":
        print("cvs_check: style check violation in %s" % filename, file=sys.stderr)
        sys.exit(1)
