#!/bin/bash
# ******************************************************************************
# Argon Design Ltd. Project P9000 Argon
# (c) Copyright 2017 Argon Design Ltd. All rights reserved.
#
# Module : maybot
# Author : Steve Barlow
# $Id: run.sh 18332 2017-06-18 16:18:38Z sjb $
# ******************************************************************************

# run.sh - Start local server

# Opens two terminal windows - one for web server and one for ngrok
gnome-terminal -x ./maybot.py
gnome-terminal -x ngrok http -subdomain maybot-alexa -region eu 5001
