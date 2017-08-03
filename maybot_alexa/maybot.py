#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ******************************************************************************
# Argon Design Ltd. Project P9000 Argon
# (c) Copyright 2017 Argon Design Ltd. All rights reserved.
#
# Module : maybot
# Author : Steve Barlow
# $Id: maybot.py 18445 2017-06-22 08:40:03Z sjb $
# ******************************************************************************

"""Skill for Amazon Alexa that completes sentences in the style of Theresa May.

Political Theresa is a skill for Amazon Alexa that completes sentences in the
style of Theresa May's parliamentary spoken contributions scraped from Hansard
from given starting words. This code forms a web server which responds to JSON
service requests from Alexa and returns a JSON response with the text to be
spoken.
"""

from __future__ import print_function
from flask import Flask, request, render_template
from flask_ask import Ask, question, statement
import time
import os
import logging
from model.create_sentence import create_sentence

app = Flask(__name__)
ask = Ask(app, '/')

welcome_text  = "Hi! I'm a neural network that completes a sentence in the style of Theresa May. "\
                "What are the first few words of the sentence you'd like me to complete?"

reprompt_text = "Please give me the first few words of a sentence to finish."

goodbye_text  = "Goodbye from Political Theresa."

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

@ask.launch
def launch():
    return question(welcome_text).reprompt(reprompt_text).simple_card('Welcome', welcome_text)

@ask.intent('CompleteSentenceIntent')
def complete(InitialWords):
    if InitialWords is None:
        InitialWords = ''
    t1 = time.time()
    speech_output = create_sentence(InitialWords, seed=0, diversity=0.0)
    t2 = time.time()
    log('CompleteSentenceIntent "{0}" -> "{1}" Response time = {2:.1f}s'.format(
        InitialWords.encode('utf-8'), speech_output.encode('utf-8'), t2-t1))
    speech_utf8 = speech_output.encode('utf-8')
    return statement(speech_utf8).simple_card('Completed Sentence', speech_utf8)

@ask.intent('AMAZON.HelpIntent')
def help():
    return question(reprompt_text).reprompt(reprompt_text).simple_card('Help', reprompt_text)

@ask.intent('AMAZON.StopIntent')
def stop():
    return goodbye()

@ask.intent('AMAZON.CancelIntent')
def cancel():
    return goodbye()

def goodbye():
    return statement(goodbye_text).simple_card('Session Ended', goodbye_text)

@ask.session_ended
def session_ended():
    return '{}', 200

if __name__ == '__main__':
    setUpLogging()
    app.run(debug=False, port=5001)
