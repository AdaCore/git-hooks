#! /usr/bin/env python
"""A dummy cvs_check program that FAILs all files.
"""
from __future__ import print_function
import sys

# To help with testing, print a trace containing the name of the module
# and the names of the files being checked.
print(
    "cvs_check: %s < %s"
    % (
        " ".join(["`%s'" % arg for arg in sys.argv[1:]]),
        " ".join(["`%s'" % arg for arg in sys.stdin.read().splitlines(False)]),
    )
)

filenames = sys.stdin.read().splitlines(False)

print(
    "ERROR: %s: Copyright year in header is not up to date" % filenames[0],
    file=sys.stderr,
)
sys.exit(1)
