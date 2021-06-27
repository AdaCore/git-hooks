#! /usr/bin/env python
"""A dummy cvs_check that pretends that certain files fail the style check.

It also prints a trace on stdout, in order to allow us to allow us
to verify that the script was called with the correct arguments.
"""
from __future__ import print_function
import sys

filenames = sys.stdin.read().splitlines(False)
assert filenames

# Fail the style-check.
print(
    "ERROR: %s: Copyright year in header is not up to date" % filenames[0],
    file=sys.stderr,
)
sys.exit(1)
