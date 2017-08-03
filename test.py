#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ******************************************************************************
# Argon Design Ltd. Project P9000 Argon
# (c) Copyright 2017 Argon Design Ltd. All rights reserved.
#
# Module : maybot
# Author : Steve Barlow
# $Id: test.py 18332 2017-06-18 16:18:38Z sjb $
# ******************************************************************************

from __future__ import print_function
from model.create_sentence import create_sentence

input_words = 'The right honourable gentleman'
print(create_sentence(input_words, seed=0, diversity=0.0))


