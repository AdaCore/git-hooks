#! /usr/bin/env python
"""A dummy cvs_check program that fails all files.
"""
import sys

for arg in sys.stdin.read().splitlines(False):
    print "%s: bad style, please fix." % arg
sys.exit(1)
