#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ******************************************************************************
# Argon Design Ltd. Project P9000 Argon
# (c) Copyright 2017 Argon Design Ltd. All rights reserved.
#
# Module : hansard_scrape
# Author : Steve Barlow
# $Id: check_chars.py 18332 2017-06-18 16:18:38Z sjb $
# ******************************************************************************

"""Check characters in contribution file.

Usage: ./check_chars.py <json_filename>
"""

import json
import sys

allowed_special_chars = u' !#$%\',-./?@\u00a3\u201c\u201d\u20ac' # Unicode chars are "£“”€"

if len(sys.argv) != 2:
    print 'Usage: ./check_chars.py <json_filename>'
    sys.exit(1)

filename = sys.argv[1]

with open(filename, 'rt') as f:
    contributions = json.load(f)
text = ' '.join(contributions)

print 'Number of contributions =', len(contributions)
print 'Number of words         =', len(text.split())
print 'Number of characters    =', len(text)

chars = sorted(list(set(text)))
errors = 0
for c in chars:
    if c.isalnum() == False and c not in allowed_special_chars:
        print 'Non-allowed character', repr(c), '(\'' + c.encode('utf-8') + '\')'
        errors += 1

if errors:
    sys.exit(1)
