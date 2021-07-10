#! /usr/bin/env python
from __future__ import print_function
import sys

ML_MAP = {
    "bfd": "bfd-cvs@example.com",
    "gdb": "gdb-cvs@example.com",
}

EVERYONE = set(ML_MAP[ml_key] for ml_key in ML_MAP)

OWNER_MAP = (
    ("bfd/", "bfd"),
    ("opcode/", "bfd"),
    ("gdb/", "gdb"),
)


def ml_from_filename(filename):
    for (path, ml_key) in OWNER_MAP:
        if filename.startswith(path):
            return ML_MAP[ml_key]
    # Not found in map, it is a common file.
    return EVERYONE


result = set()
for filename in sys.stdin:
    ml = ml_from_filename(filename)
    if isinstance(ml, str):
        result.add(ml)
    else:
        result.update(ml)
    if len(result) >= len(EVERYONE):
        # We have iterated over enough entries to know already
        # that we have selected all possible recipients. So
        # stop now.
        break

if not result:
    # No files given, return EVERYONE
    result = EVERYONE

print("\n".join(sorted(result)))
