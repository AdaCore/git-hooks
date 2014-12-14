#! /usr/bin/env python
import sys

BFD_ML = 'bfd-cvs@example.com'
GDB_ML = 'gdb-cvs@example.com'
EVERYONE = (BFD_ML, GDB_ML)

OWNER_MAP = (
    ('bfd/', BFD_ML),
    ('opcode/', BFD_ML),
    ('gdb/', GDB_ML),
    )


def ml_from_filename(filename):
    for (path, ml) in OWNER_MAP:
        if filename.startswith(path):
            return ml
    # Not found in map, it is a common file.
    return EVERYONE

result = set()
for filename in sys.stdin:
    ml = ml_from_filename(filename)
    if isinstance(ml, basestring):
        result.add(ml)
    else:
        result.update(ml)
    if len(result) >= 2:
        # We have iterated over enough entries to know already
        # that we have selected all possible recipients. So
        # stop now.
        break

if not result:
    # No files given, return EVERYONE
    result = EVERYONE

print '\n'.join(result)
