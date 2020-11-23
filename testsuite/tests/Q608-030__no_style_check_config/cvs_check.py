#! /usr/bin/env python
"""A dummy cvs_check program that fails all files.
"""
from __future__ import print_function
import sys

for arg in sys.stdin.read().splitlines(False):
    print("%s: bad style, please fix." % arg)
sys.exit(1)
