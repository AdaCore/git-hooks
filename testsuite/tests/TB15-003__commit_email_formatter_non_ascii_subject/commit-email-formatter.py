#! /usr/bin/env python
import sys
import json

json.dump({'email_subject': u'My \u2192 Email Subject \u2190'}, sys.stdout)
