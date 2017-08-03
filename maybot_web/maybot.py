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

"""Web app that completes sentences in the style of Theresa May.

Maybot is a recurrent neural network that completes sentences in the style of
Theresa May's parliamentary spoken contributions scraped from Hansard.
"""

from __future__ import print_function
from flask import Flask, request, render_template
import time
import os
import logging
from model.create_sentence import create_sentence

app = Flask(__name__)

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

@app.route('/', methods=['POST', 'GET'])
def handle_maybot():
    if 'initialWords' in request.values:
        initialWords = request.values['initialWords']
        t1 = time.time()
        result = create_sentence(initialWords)
        t2 = time.time()
        print('Response time = {:.1f}s'.format(t2-t1))
        log('/ "{0}" -> "{1}" Response time = {2:.1f}s'.format(
            initialWords.encode('utf-8'), result.encode('utf-8'), t2-t1))
    else:
        result = ''
        log('/')
    return render_template('index.html', result=result)

@app.route('/privacy')
def handle_privacy():
    log('/privacy')
    return render_template('privacy.html')

if __name__ == '__main__':
    setUpLogging()
    app.run(debug=False)
