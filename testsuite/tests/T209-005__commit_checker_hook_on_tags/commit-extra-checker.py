#! /usr/bin/env python
import sys
import json

cli_args = sys.argv[1:]
stdin_data = sys.stdin.read()

print("DEBUG: commit-extra-checker.py {}".format(" ".join(cli_args)))
print("-----[ stdin ]-----")
print(stdin_data)
print("---[ end stdin ]---")

# Verify that the data sent via stdin is valid JSON...
json.loads(stdin_data)
if "(bad-commit)" in stdin_data:
    print("Error: Invalid bla bla bla. Rejecting Update.")
    sys.exit(1)
