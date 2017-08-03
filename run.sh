#!/bin/bash
# ******************************************************************************
# Argon Design Ltd. Project P9000 Argon
# (c) Copyright 2017 Argon Design Ltd. All rights reserved.
#
# Module : maybot
# Author : Steve Barlow
# $Id: run.sh 18334 2017-06-18 18:58:50Z sjb $
# ******************************************************************************

# run.sh - Start local server

# Opens a tabbed terminal window with 4 tabs - one for each of the servers and one for ngrok
gnome-terminal \
    --tab --title maybot_web -e maybot_web/maybot.py \
    --tab --title maybot_alexa -e maybot_alexa/maybot.py \
    --tab --title maybot_google -e maybot_google/maybot.py \
    --tab --title ngrok -x ngrok start -config ~/.ngrok2/ngrok.yml -config ngrok.yml maybot_web maybot_alexa maybot_google
