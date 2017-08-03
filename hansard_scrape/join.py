#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ******************************************************************************
# Argon Design Ltd. Project P9000 Argon
# (c) Copyright 2017 Argon Design Ltd. All rights reserved.
#
# Module : hansard_scrape
# Author : Steve Barlow
# $Id: join.py 18332 2017-06-18 16:18:38Z sjb $
# ******************************************************************************

"""Join JSON contribution files.

Usage: ./join.py <json_filename1> [<json_filename2>] ... <json_filename_out>
"""

import json
import sys

if len(sys.argv) < 3:
    print 'Usage: ./join.py <json_filename1> [<json_filename2>] ... <json_filename_out>'
    sys.exit(1)
    
out_filename = sys.argv[-1]
contributions = []

for in_filename in sys.argv[1:-1]:
    # print in_filename
    with open(in_filename, 'rt') as f:
        file_contributions = json.load(f)
    contributions.extend(file_contributions)
    
# Convert to utf-8 so JSON file can be understood more easily in a text editor
utf8_contributions = [s.encode('utf-8') for s in contributions]

with open(out_filename, 'wt') as f:
    json.dump(utf8_contributions, f, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': '))
