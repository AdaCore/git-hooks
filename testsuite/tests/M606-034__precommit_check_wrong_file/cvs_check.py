#! /usr/bin/env python
"""A dummy cvs_check program...
"""
import sys
import os.path

filenames = sys.stdin.read().splitlines(False)

# To help with testing, print a trace containing the name of the module
# and the names of the files being checked.
print(
    "cvs_check: %s < %s"
    % (
        " ".join(["`%s'" % arg for arg in sys.argv[1:]]),
        " ".join(["`%s'" % arg for arg in filenames]),
    ),
    file=sys.stderr,
)

# In this testcase, we expect the hooks to only ever call this script
# to check one file, and one file only: foo.c.  For anything else,
# pretend there is a style check failure:
for filename in filenames:
    base_filename = os.path.basename(filename)
    if base_filename != "foo.c":
        print(
            ("cvs_check ERROR: %s is missing a copyright header" % base_filename),
            file=sys.stderr,
        )
