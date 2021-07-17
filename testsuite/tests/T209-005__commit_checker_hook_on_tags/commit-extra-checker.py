#! /usr/bin/env python
import sys
import json

cli_args = sys.argv[1:]
stdin_data = sys.stdin.read()

print("DEBUG: commit-extra-checker.py {}".format(" ".join(cli_args)))
print("-----[ stdin ]-----")
checker_data = json.loads(stdin_data)
for k in sorted(checker_data.keys()):
    print("  . {}: {}".format(k, checker_data[k]))
print("---[ end stdin ]---")

if "(bad-commit)" in stdin_data:
    print("Error: Invalid bla bla bla. Rejecting Update.")
    sys.exit(1)
