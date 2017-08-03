#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ******************************************************************************
# Argon Design Ltd. Project P9000 Argon
# (c) Copyright 2017 Argon Design Ltd. All rights reserved.
#
# Module : hansard_scrape
# Author : Steve Barlow
# $Id: mp_contrib.py 18332 2017-06-18 16:18:38Z sjb $
# ******************************************************************************

"""Scrape an MP's spoken 'contributions' from Hansard.

Usage: ./mp_contrib.py <mp_name> [<list_start_page>]

Produces a JSON file containing a list. Each element is a string with one
contribution. Encoding is UTF-8. Contributions that consist of multiple paragraphs
are divided by \n. 
"""

import requests
import json
from bs4 import BeautifulSoup
import urlparse
import re
import sys

search_url = 'https://hansard.parliament.uk/search/Members'
search_params = {'searchTerm':None, 'currentFormerFilter':0, 'house':'Commons'}

list_url = 'https://hansard.parliament.uk/search/MemberContributions'
list_params = {'memberId':None, 'type':'Spoken', 'page':None}

contrib_url_base = 'https://hansard.parliament.uk'


# ---------------------------------------------------------------------------------------
# Support functions

# Special chars seen in text:
# u'\n'       ''                      Treat like space. Convert to space. Remove double spaces
# u' '        ' '                     Normal spaces. Leave as is
# u'!'        '!'                     Genuine punctuation. Treat like '.'
# u'#'        '#'                     Twitter tag. Treat like alphanumeric character and leave as is
# u'$'        '$'                     Used with numbers for dollar money amounts. Treat like alphanumeric character
# u'%'        '%'                     Percentage. Treat like alphanumeric character
# u'&'        '&'                     Used in A&E. Convert to ' and '
# u"'"        "'"                     Possessive. Only 1 occurence. Treat like alphanumeric character
# u'('        '('                     Used to give name after constituency "Blackburn (Mr Straw)"
#                                     Also numbered points (1)
#                                     Also one case of "(Recall of MPs Bill (Programme))"
# u')'        ')'                     Ignore between '(' and ')'
# u'*'        '*'                     Used in grade A*. Convert to ' star'
# u'+'        '+'                     Used in 'million+'. Convert to ' plus'
# u','        ','                     Normal punctuation. Leave as is
# u'-'        '-'                     Used for hyphenated words. Treat like alphanumeric character
# u'.'        '.'                     Normal punctuation. Leave as is
# u'/'        '/'                     Used in 9/11 and opt-in/opt-out. Leave as is. Alexa copes
# u':'        ':'                     Used as punctuation. Convert to '.'
# u';'        ';'                     Used as punctuation. Convert to '.'
# u'?'        '?'                     Normal punctuation. Leave as is
# u'@'        '@'                     Used in email addresses and twitter handles. Leave as is
# u'['        '['                     Used for [Interruption.], [Hon. Members: “Hear, hear.] etc.
# u']'        ']'                     Ignore between '[' and ']'
# u'\u00a0'   ' '                     Non-breaking space. Treat like space. Convert to space
# u'\u00a3'   '£'                     Used with numbers for money amounts. Treat like alphanumeric character
# u'\u00b8'   '¸'                     Cedilla. Occasionally used in error instead of comma. Convert to ','
# u'\u2013'   '–'                     Used as –– at start and end of aside comment. Convert to ','. Remove double commas
# u'\u2014'   '—'                     Used at start and end of aside comment. Convert to ','
# u'\u2018'   left quote '‘'          Start of reported speech or document amendment text. Convert to '“'
#                                     One case of Government‘s which should be an apostrophe
# u'\u2019'   right quote '’'         End of reported speech or document amendment text. Convert to '”'
#                                     Some cases of Government’s or womens’ etc which should be an apostrophe
# u'\u201c'   left double quote '“'   Start of reported speech. Leave as is
# u'\u201d'   right double quote '”'  End of reported speech. Leave as is
# u'\u2026'   '…'                     Used for various pauses. Convert to ',', but this isn't always right
# u'\u20ac'   '€'                     Used with numbers for money amounts. Treat like alphanumeric character

def modify_chars(text):
    text = re.sub('\([^)0-9]*?\)', '', text)
    text = re.sub('\([^)0-9]*?\)', '', text)
    text = re.sub('[()]', '', text)
    text = re.sub('\[.*?\]', '', text, flags=re.DOTALL)
    text = re.sub(u'\u00b8', ',', text)
    text = re.sub(u'(\w)[\u2018\u2019]s', '\g<1>\'s', text)
    text = re.sub(u's\u2019\s', 's\' ', text)
    text = re.sub(u'\u2018', u'\u201c', text)
    text = re.sub(u'\u2019', u'\u201d', text)
    text = re.sub(u'\u2013+', u'\u2013', text)
    text = re.sub(u'[\u2013\u2014\u2026]', ',', text)
    text = re.sub(u'[\u2026]', ',', text)
    text = re.sub(',+', ',', text)
    text = re.sub('[:;]', '.', text)
    text = re.sub(u'\xa0', ' ', text)
    text = re.sub('\s+', ' ', text)
    text = re.sub('\s([.?,!])', '\g<1>', text)
    text = text.strip()
    return text

def fix_abbreviations(text):
    text = text.replace('&', ' and ')
    text = text.replace('hon.', 'honourable')
    text = text.replace('Hon.', 'Honourable')
    text = text.replace(u'\u00b0', ' degrees') # '°'
    text = text.replace('*', ' star')
    text = text.replace('+', ' plus')
    return text

def ignored_contrib(text):
    ignored_contribs = ['rose,', 'indicated dissent.']
    return text in ignored_contribs


# ---------------------------------------------------------------------------------------
# Main code

requests.packages.urllib3.disable_warnings()

# Read command line args
if len(sys.argv) < 2 or len(sys.argv) > 3:
    print 'Usage: ./mp_contrib.py <mp_name> [<list_start_page>]'
    sys.exit(1)

mp_name = sys.argv[1]
mp_name_underscore = re.sub('\s+', '_', mp_name)
if len(sys.argv) == 3:
    start_page = int(sys.argv[2])
    filename_page_mod = '_p{0}'.format(start_page)
else:
    start_page = 1
    filename_page_mod = ''

# Search for MP by name
search_params['searchTerm'] = mp_name
r = requests.get(search_url, params=search_params)
soup = BeautifulSoup(r.text, 'html.parser')

# Find member ID
members = soup.find_all('div', 'col-sm-6 result-outer')
if len(members) != 1:
    print 'Search returned {0} results - giving up'.format(len(members))
    sys.exit(1)
member_id = int(urlparse.parse_qs(members[0].a['href'])[u'/search/MemberContributions?memberId'][0])
print 'Member ID =', member_id

# Process pages of contribution list one by one
contrib_texts = []
list_params['memberId'] = member_id
page = start_page
while True:
    print 'Page', page

    list_params['page'] = page
    r = requests.get(list_url, params=list_params)

    # DEBUG - Output list page to a file
    # with open('page.txt', 'wt') as f:
    #     f.write(r.text.encode('utf-8'))

    soup = BeautifulSoup(r.text, 'html.parser')
    contribs = soup.find_all('div', 'col-sm-12 result-outer')
    if contribs == []:
        # We've got to an empty page, so the end of the list
        break

    for contrib in contribs:
        contrib_url = contrib_url_base + contrib.a['href']        

        # Read the individual contribution page
        url, contrib_id = contrib_url.split('#')
        print contrib_id

        contrib_section = None
        attempts = 0
        while contrib_section is None and attempts < 10:
            r = requests.get(url)

            # DEBUG - Output contribution page to a file
            # with open('page.txt', 'wt') as f:
            #     f.write(r.text.encode('utf-8'))

            soup = BeautifulSoup(r.text, 'html.parser')
            contrib_section = soup.find('li', id=contrib_id)

            if contrib_section is None:
                print 'Cannot find contrib_id in page. Reloading...'
                attempts += 1

        if contrib_section is None:
            print 'Failed to find contrib_id in page 10 times. Giving up and moving on to next contribution'
            # DEBUG - If contribution is missing from page, dump it so I can see why
            # print 'URL =', contrib_url
            # with open('page.txt', 'wt') as f:
            #     f.write(r.text.encode('utf-8'))
            continue

        paras = contrib_section.find_all('p')
        assert len(paras) != 0
        paras_text = [p.get_text() for p in paras]
        text = '\n'.join(paras_text)

        # Remove question decoration
        text1 = re.sub('^Q\d+\. *', '', text)
        text2 = re.sub(' *\[\d+\]', '', text1)
        
        # Run character and other fixes
        text3 = modify_chars(text2)
        text4 = fix_abbreviations(text3)
        # Convert to utf-8 so JSON file can be understood more easily in a text editor
        text5 = text4.encode('utf-8')

        if not ignored_contrib(text5):
            contrib_texts.append(text5)

    # Output contributions as JSON. Update after every page in case something goes wrong
    filename = '{0}_contributions{1}.json'.format(mp_name_underscore, filename_page_mod)
    with open(filename, 'wt') as f:
        json.dump(contrib_texts, f, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': '))

    page += 1
