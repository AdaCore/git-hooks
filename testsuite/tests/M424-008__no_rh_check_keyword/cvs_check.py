#! /usr/bin/env python
"""A dummy cvs_check program that passes all files.

It also prints a trace on stdout, in order to allow us to allow us
to verify that the script was called with the correct arguments.
"""
import sys

filenames = sys.stdin.read().splitlines(False)

# To help with testing, print a trace containing the name of the module
# and the names of the files being checked.
print(
    "cvs_check: %s < %s"
    % (
        " ".join(["`%s'" % arg for arg in sys.argv[1:]]),
        " ".join(["`%s'" % arg for arg in filenames]),
    )
)

# Fail the style-check for the following files:
for filename in filenames:
    if filename == "b":
        print("*** cvs_check: some style errors in: %s" % filename)
        sys.exit(1)
