#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ******************************************************************************
# Argon Design Ltd. Project P9000 Argon
# (c) Copyright 2017 Argon Design Ltd. All rights reserved.
#
# Module : sjb_word_model
# Author : Steve Barlow
# $Id: create_sentence.py 18332 2017-06-18 16:18:38Z sjb $
# ******************************************************************************

"""Complete a sentence in the style of Theresa May's spoken contributions in parliament.

Use the function create_sentence() to create a sentence from given starting words.

Example:
>>> from create_sentence import create_sentence
>>> print(create_sentence('Brexit means', 0))
Brexit means i am very pleased to say that my right honourable friend the current
home secretary is taking that same passion to ensuring that the voices of the
victims of crime are heard and is taking that forward. i recognise, obviously,
the interest and the attention that the right honourable gentleman has given to
these issues, of course, he is a former health minister, and i would be happy
to meet him and others, as he suggests.
"""

from __future__ import print_function
from keras.models import load_model
import json
import pickle
import gensim as gs
import numpy as np
import os
import sys
import time

myDir = os.path.dirname(os.path.realpath(__file__)) + '/'

vmodel = gs.models.Word2Vec.load(myDir + 'vmodel')
with open(myDir + 'codetables.pickle', 'rb') as f:
    wordCoding, codedWord = pickle.load(f)

wordvec_dim = len(vmodel['.'])  # Length of word vector - nominally 300
sd_len = 12                     # Number of words in model input pattern

# N.B. Need to make sure that Flask runs subsequent calls to create_sentence() in the same thread
# as this initialisation otherwise TF will fail with 'ValueError: Tensor Tensor("Softmax:0", ...'
# That seems to require that Flask is run with debug=False
import threading
init_thread = threading.current_thread()

model = load_model(myDir + 'trained_model.h5')

# Support functions

def prepare_text(text):
    # Helper function to take input text and prepare it into tokenised words to be used with model
    text = text.lower()
    # Separate punctuation so it becomes separate tokens
    text = text.replace('.', ' . ')
    text = text.replace('!', ' ! ')
    text = text.replace('?', ' ? ')
    text = text.replace(',', ' , ')
    text = text.replace(u'\u201c', u' \u201c ') # Left double quote '“'
    text = text.replace(u'\u201d', u' \u201d ') # Right double quote '”'
    parsedWords = text.split()
    return parsedWords

def sample(a, temperature=1.0):
    # Helper function to sample an index from a probability array
    if temperature == 0.0:
        return np.argmax(a)
    np.random.random() # Make sure RNG initialised consistently
    a = np.clip(a, 1E-20, 1.0) # Make sure we don't have any zeros
    a = np.exp(np.log(a) / temperature)
    a = a / np.sum(a)
    a = a * 0.999999 # Added to fix sum(pvals[:-1]) > 1.0 error
    return np.argmax(np.random.multinomial(1, a, 1))


# ---------------------------------------------------------------------------------------
# Core function

def create_sentence(input_text, seed=None, diversity=0.0):
    """Create a sentence from given starting words.
    
    'input_words' is a string with the starting words. This can be empty, a single word or several words starting a
    sentence. Upper case and punctuation are allowed. 'seed' is a number to initialise a random number generator.
    Set this to a fixed value for repeatable behaviour or None for random operation. The generated sentence
    including the initial words is returned as a string. This is all lower case with the only punctuation used being
    ',', '.', '?', '!', '“' and '”'. 
    """

    assert threading.current_thread() == init_thread
    
    t1 = time.time()

    np.random.seed(seed)

    words = prepare_text(input_text)
    correct_num_words = (['.'] * sd_len + words)[-sd_len:]
    
    vecsentence = [vmodel[w] if w in vmodel else vmodel['.'] for w in correct_num_words]
    
    output = input_text
    for i in range(100):
        preds = model.predict(np.reshape(vecsentence, (1,-1)), verbose=0)[0]
        wcode = sample(preds, diversity)
        word = codedWord[wcode]
        prev_word = output[-1] if output != '' else None
        if prev_word not in [None, u'\u201c'] and word not in ['.', '!', '?', ',', u'\u201d']:
            output += ' '
        output += word
        vecsentence = vecsentence[1:] + [vmodel[word]]
        if i > 20 and word in ['.', '!', '?']:
            break

    t2 = time.time()
    #print('Response time = {:.1f}s'.format(t2-t1))
    
    return output


# ---------------------------------------------------------------------------------------
# Main code (for testing)

if __name__ == '__main__':

    if len(sys.argv) > 1:
        # Use the supplied arguments as input sentences to complete
        for input_words in sys.argv[1:]:
            print(create_sentence(input_words, seed=0, diversity=0.0))
            print()
    else:
        # Complete these standard examples
        input_words = 'The right honourable gentleman'
        print(create_sentence(input_words, seed=0, diversity=0.0))
        print()
        input_words = 'Brexit means'
        print(create_sentence(input_words, seed=0, diversity=0.0))
