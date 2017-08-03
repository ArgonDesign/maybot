#!/bin/bash
# ******************************************************************************
# Argon Design Ltd. Project P9000 Argon
# (c) Copyright 2017 Argon Design Ltd. All rights reserved.
#
# Module : hansard_scrape
# Author : Steve Barlow
# $Id: post_process.sh 18332 2017-06-18 16:18:38Z sjb $
# ******************************************************************************

rm -f all_contributions.json
rm -f other_contributions.json

ALL_CONTRIB=`ls *.json`
OTHER_CONTRIB=${ALL_CONTRIB/theresa_may_contributions.json/}

for CONTRIB in $ALL_CONTRIB
do
    echo $CONTRIB
    ./check_chars.py $CONTRIB || exit 1
done

./join.py $OTHER_CONTRIB other_contributions.json
./join.py $ALL_CONTRIB all_contributions.json

echo
echo "Total:"
./check_chars.py all_contributions.json