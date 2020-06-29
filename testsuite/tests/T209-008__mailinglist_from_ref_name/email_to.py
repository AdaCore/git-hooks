#! /usr/bin/env python
import sys

ref_name = sys.argv[1]
if sys.argv[1].startswith('refs/heads/release-'):
    print('release-commits@example.com')
else:
    print('devel-commits@example.com')
