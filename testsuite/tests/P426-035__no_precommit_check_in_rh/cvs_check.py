#! /usr/bin/env python
"""A dummy cvs_check program that passes all files.
"""
# There should not be any file to check, so this script should never
# be called. Return an error if it happens.
import sys

print('ERROR: cvs_check called for file: %s' % sys.argv[1])
sys.exit(1)
