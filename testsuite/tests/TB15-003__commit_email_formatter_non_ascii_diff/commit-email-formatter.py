#! /usr/bin/env python
import sys
import json

json.dump({'diff': u'My \u2192 Email diff \u2190\n'}, sys.stdout)
