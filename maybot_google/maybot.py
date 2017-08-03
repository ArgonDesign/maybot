#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ******************************************************************************
# Argon Design Ltd. Project P9000 Argon
# (c) Copyright 2017 Argon Design Ltd. All rights reserved.
#
# Module : maybot
# Author : Steve Barlow
# $Id: maybot.py 18334 2017-06-18 18:58:50Z sjb $
# ******************************************************************************

"""Action for Google Assistant that completes sentences in the style of Theresa May.

Maybot is an action for Google Assistant that completes sentences in the style of
Theresa May's parliamentary spoken contributions scraped from Hansard from given
starting words. This code forms a web server which responds to JSON service
requests from Google Assistant and returns a JSON response with the text to be spoken.
"""

# For flask_assistant see https://github.com/treethought/flask-assistant

from __future__ import print_function
from flask import Flask, request
from flask_assistant import Assistant, ask, tell
import time
import os
import logging
from model.create_sentence import create_sentence

app = Flask(__name__)
assist = Assistant(app, route='/')

def setUpLogging():
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'maybot.log')
    print('Logging to {0} / maybot.log.1'.format(filename))
    logHandler = logging.handlers.RotatingFileHandler(filename, maxBytes=100*1024*1024, backupCount=1) 
    logHandler.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(asctime)s] - %(levelname)s - %(message)s', '%d/%b/%Y %H:%M:%S')
    logHandler.setFormatter(formatter)
    app.logger.addHandler(logHandler)
    app.logger.setLevel(logging.INFO)
    # Werkzeug logging still comes out to stdout
 
def log(text):
    if 'X-Forwarded-For' in request.headers:
        ip = request.headers['X-Forwarded-For']
    else:
        ip = request.remote_addr
    app.logger.info('{0:15} {1}'.format(ip, text))

@assist.action('CompleteSentenceIntent')
def complete(InitialWords):
    t1 = time.time()
    speech = create_sentence(InitialWords, seed=0, diversity=0.0)
    t2 = time.time()
    log('CompleteSentenceIntent "{0}" -> "{1}" Response time = {2:.1f}s'.format(
        InitialWords.encode('utf-8'), speech.encode('utf-8'), t2-t1))
    return tell(speech)

if __name__ == '__main__':
    setUpLogging()
    app.run(debug=False, port=5002)
