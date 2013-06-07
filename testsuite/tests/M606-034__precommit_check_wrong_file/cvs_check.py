#! /usr/bin/env python
"""A dummy cvs_check program...
"""
import sys
import os.path

# Print a debug trace, to start...
print >> sys.stderr, 'cvs_check: %s' % sys.argv[1]

# In this testcase, we expect the hooks to only ever call this script
# to check one file, and one file only: foo.c.  For anything else,
# pretend there is a style check failure:
base_filename = os.path.basename(sys.argv[1])
if base_filename != 'foo.c':
    print >> sys.stderr, ('cvs_check ERROR: %s is missing a copyright header'
                          % base_filename)
