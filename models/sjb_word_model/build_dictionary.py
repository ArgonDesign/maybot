#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ******************************************************************************
# Argon Design Ltd. Project P9000 Argon
# (c) Copyright 2017 Argon Design Ltd. All rights reserved.
#
# Module : sjb_word_model
# Author : Steve Barlow
# $Id: build_dictionary.py 18332 2017-06-18 16:18:38Z sjb $
# ******************************************************************************

"""Build dictionary from complete corpus."""

from __future__ import print_function
import json
import pickle
import re
import gensim as gs

# For details of Gensim word2vec see:
# https://radimrehurek.com/gensim/models/word2vec.html 

# Load text and covert to lowercase
filename = 'all_contributions.json'
with open(filename, 'rt') as f:
    contributions = json.load(f)
text = ' '.join(contributions)

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
parsedWords = [sentence.split() for sentence in non_empty_sentences]
flatWords = [word for sentence in parsedWords for word in sentence]

# DEBUG - Output flatWords as a JSON file
# Useful to see how specific parsed word mistakes arise
# json_string = json.dumps(flatWords, f, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': '))
# with open('flatWords.txt', 'wt') as f:
#     f.write(json_string.encode('utf-8'))

wordCoding = {}
wordCount = {}
codedWord = {}
codeNum = 0
for word in flatWords:
    if not word in wordCoding:
        wordCoding[word] = codeNum
        codedWord[codeNum] = word
        codeNum += 1
        wordCount[word] = 1
    else:
        wordCount[word] += 1

print('Corpus length in words:', len(flatWords))
print('Distinct words:', len(wordCoding))

# DEBUG - Output word counts as a JSON file
# Useful to see why there are so many distinct words
json_string = json.dumps(wordCount, f, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': '))
with open('wordCount.txt', 'wt') as f:
    f.write(json_string.encode('utf-8'))

codeTables = (wordCoding, codedWord)
with open('codetables.pickle', 'wb') as f:
    pickle.dump(codeTables, f)

vmodel = gs.models.Word2Vec(parsedWords, size=300, min_count=1, iter=10, window=8, sg=1, hs=0, negative=5)
vmodel.save('vmodel')
