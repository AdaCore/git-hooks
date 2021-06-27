#! /usr/bin/env python
import sys
import json

json.dump({"email_body": u"My \u2192 Email body \u2190\n"}, sys.stdout)
