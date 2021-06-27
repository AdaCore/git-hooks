#! /usr/bin/env python
"""A dummy cvs_check program that passes all files.

It also prints a trace on stdout, in order to allow us to get a trace
of which files each commit modifies/adds and their path length.
"""
import sys

for arg in sys.stdin.read().splitlines(False):
    arg_len = len(arg)
    print("cvs_check: `{arg}' ({arg_len} chars)".format(arg=arg, arg_len=arg_len))
