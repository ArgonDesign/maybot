#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ******************************************************************************
# Argon Design Ltd. Project P9000 Argon
# (c) Copyright 2017 Argon Design Ltd. All rights reserved.
#
# Module : sjb_word_model
# Author : Steve Barlow
# $Id: train.py 18332 2017-06-18 16:18:38Z sjb $
# ******************************************************************************

"""Train DNN to generare text in style of Theresa May."""

from __future__ import print_function
from keras.models import Sequential, load_model
from keras.layers import Dense, Activation, Dropout, ELU
from keras.optimizers import Adagrad
from keras.callbacks import TensorBoard
import json
import pickle
import re
import random
import gensim as gs
import numpy as np
import os
import sys
import datetime

# Load coding
vmodel = gs.models.Word2Vec.load('vmodel')
with open('codetables.pickle', 'rb') as f:
    wordCoding, codedWord = pickle.load(f)

wordvec_dim = len(vmodel['.']) # Length of word vector - nominally 300
sd_len = 12
dense_dim = 1500
batch_size = 256

# Load training text
if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    filename = 'other_contributions.json'
with open(filename, 'rt') as f:
    contributions = json.load(f)

# Shuffle contributions so validation split doesn't work just with oldest contributions
random.seed(0)
random.shuffle(contributions)
text = ' '.join(contributions)

# !!! Shorten text for faster training - break at full stop
# text = text[:50000].rpartition('.')[0] + '.'

# Divide into sentences and separate punctuation so it becomes separate tokens
# Other special characters stay as part of words
text = text.lower()
text = re.sub('(\d)\.(\d)', '\g<1><point>\g<2>', text) # Distinguish decimal point
text = text.replace('.', ' . <sentence-sep>')
text = re.sub('<point>', '.', text)
text = text.replace('!', ' ! <sentence-sep>')
text = text.replace('?', ' ? <sentence-sep>')
text = re.sub('(\d),(\d)', '\g<1><comma>\g<2>', text) # Distinguish thousands separator
text = text.replace(',', ' , ')
text = re.sub('<comma>', ',', text)
text = text.replace(u'\u201c', u' \u201c ') # Left double quote '“'
text = text.replace(u'\u201d', u' \u201d ') # Right double quote '”'

sentences = text.split('<sentence-sep>')
non_empty_sentences = filter(len, sentences)
parsed_sentences = [sentence.split() for sentence in non_empty_sentences]

print('Vectorisation...')
x_vals = []
y_vals = []
n_sentences = len(parsed_sentences)
print('n_sentences =', n_sentences)

for i, s in enumerate(parsed_sentences):
    # Pad start of each sentence with sd_len-1 '.'s used as nulls
    pre = ['.'] * (sd_len-1)
    # Pad end of each sentence with npost words from following sentences
    post = []
    # ... if sentence ends in '.' need one less because this duplicates a pad case in the following sentence
    npost = sd_len-1 if s[-1] == '.' else sd_len
    j = i + 1
    while len(post) < npost and j < n_sentences:
        post.extend(parsed_sentences[j])
        j += 1
    post = post[0:npost]
    # Combine and generate vectors
    s = pre + s + post
    for k in range(len(s) - sd_len):
        x_vals.append(s[k:k+sd_len])
        y_vals.append(s[k+sd_len])
num_vecs = len(x_vals)

# DEBUG - Output initial vectors as a text file
# with open('vectors.txt', 'wt') as f:
#     for i in range(500):
#         for w in x_vals[i]:
#             f.write('{0:12} '.format(w))
#         f.write('-> ' + y_vals[i] + '\n')
# sys.exit(0)

# Round down to multiple of batch_size and ignore excess
num_vecs = (num_vecs // batch_size) * batch_size
print('x_D shape:', str((num_vecs, sd_len * wordvec_dim)))
print('y_D shape:', str((num_vecs, len(wordCoding))))

def one_hot(index):
    retVal = np.zeros((len(wordCoding)), dtype=np.bool)
    retVal[index] = 1
    return retVal

def make_xy(start_idx, num):
    x_D = np.zeros((num, sd_len * wordvec_dim))
    y_D = np.zeros((num, len(wordCoding)))
    for idx in range(num):
        input_words = x_vals[start_idx + idx]
        x_D[idx] = np.ravel([vmodel[w] for w in input_words])
        output_word = y_vals[start_idx + idx]
        y_D[idx] = one_hot(wordCoding[output_word])
    return x_D, y_D

train_num_vecs = (int(0.7 * num_vecs) // batch_size) * batch_size
val_num_vecs = num_vecs - train_num_vecs
print('train_num_vecs =', train_num_vecs)
print('val_num_vecs =', val_num_vecs)

def train_xy_generator():
    start_idx = 0
    while 1:
        yield make_xy(start_idx, batch_size)
        start_idx += batch_size
        if start_idx >= train_num_vecs:
            start_idx = 0
            
def val_xy_generator():
    start_idx = 0
    while 1:
        yield make_xy(train_num_vecs + start_idx, batch_size)
        start_idx += batch_size
        if start_idx >= val_num_vecs:
            start_idx = 0

# Build the model

# Load existing model if there is one
if os.path.isfile('trained_model.h5'):
    print('Loading existing model and weights...')
    model = load_model('trained_model.h5')

else:
    print('Building model...')
    model = Sequential()
    model.add(Dense(dense_dim, input_dim=sd_len * wordvec_dim))
    model.add(ELU())
    model.add(Dropout(0.2))
    model.add(Dense(dense_dim))
    model.add(ELU())
    model.add(Dropout(0.2))
    model.add(Dense(dense_dim))
    model.add(ELU())
    model.add(Dropout(0.2))
    model.add(Dense(len(wordCoding)))
    model.add(Activation('softmax'))
    model.summary()

    optimiser = Adagrad(lr=0.002) # 0.001
    model.compile(optimiser, loss='categorical_crossentropy')

# Train the model, output generated text after each iteration

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

def strSentence(sentence):
    result = ''
    prev_word = None
    for word in sentence:
        if prev_word not in [None, u'\u201c'] and word not in ['.', '!', '?', ',', u'\u201d']:
            result += ' '
        result += word
        prev_word = word
    return result

callbacks_list = []

# DEBUG - Save logs for Tensorboard - found not to be very helpful
# tb = TensorBoard()
# callbacks_list.append(tb)

# See what validation loss is before training
print('Calculating initial validation loss...')
result = model.evaluate_generator(val_xy_generator(), val_num_vecs)
print('initial val_loss = {0:.4f}'.format(result))

try:
    for iteration in range(200):
        print()
        print('-' * 50)
        
        history = model.fit_generator(train_xy_generator(), train_num_vecs, nb_epoch=5,
            validation_data = val_xy_generator(), nb_val_samples = val_num_vecs, callbacks=callbacks_list)
        loss = history.history['loss'][-1]
        val_loss = history.history['val_loss'][-1]
        
        print('Saving trained model')
        model.save('trained_model.h5')

        x_D, y_D = make_xy(0, 5000)
        preds = model.predict(x_D, verbose=0)
        train_accuracy = np.mean(np.equal(np.argmax(y_D, axis=-1), np.argmax(preds, axis=-1))) * 100.0
        print('Training accuracy = {0:.2f}%'.format(train_accuracy))

        x_D, y_D = make_xy(num_vecs - 5000, 5000)
        preds = model.predict(x_D, verbose=0)
        test_accuracy = np.mean(np.equal(np.argmax(y_D, axis=-1), np.argmax(preds, axis=-1))) * 100.0
        print('Test accuracy = {0:.2f}%'.format(test_accuracy))
        
        with open('training_log.txt', 'at') as f:
            print(datetime.datetime.now(), file = f, end='  ')
            print('iteration = {0:03d}'.format(iteration), file=f, end=', ')
            print('loss = {0:.4f}'.format(loss), file=f, end=', ')
            print('val_loss = {0:.4f}'.format(val_loss), file=f, end=', ')
            print('training accuracy = {0:5.2f}%'.format(train_accuracy), file=f, end=', ')
            print('test accuracy = {0:5.2f}%'.format(test_accuracy), file=f)

        # Save model snapshots in case training falls off
        model.save('trained_model_{0:03d}_{1:.4f}.h5'.format(iteration, train_accuracy))

        seed_index = np.random.randint(0, num_vecs)
        print()
        for diversity in [0.0, 0.25, 0.5]:
            print('----- diversity:', diversity)

            sentence = x_vals[seed_index]
            print('----- Generating with seed: "' + strSentence(sentence) + '"')

            prev_word = None
            for i in range(100):
                vecsentence = [vmodel[word] for word in sentence]
                preds = model.predict(np.reshape(vecsentence, (1,-1)), verbose=0)[0]
                wcode = sample(preds, diversity)
                word = codedWord[wcode]
                
                sentence = np.append(sentence[1:], word)
                if prev_word not in [None, u'\u201c'] and word not in ['.', '!', '?', ',', u'\u201d']:
                    sys.stdout.write(' ')
                sys.stdout.write(word)
                sys.stdout.flush()
                prev_word = word
            print()
except KeyboardInterrupt:
    print('Keyboard interrupt')
    sys.exit(0)
