#! /usr/bin/env python
"""A dummy cvs_check program that passes all files.
"""
from __future__ import print_function
# There should not be any file to check, so this script should never
# be called. Return an error if it happens.
import sys

print(('ERROR: cvs_check called for file(s): %s' %
      ' '.join(["`%s'" % arg for arg in sys.stdin.read().splitlines(False)])))
sys.exit(1)
