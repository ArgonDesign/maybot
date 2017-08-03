hansard_scrape
==============

This directory contains Python tools to scrape MPs spoken contributions from Hansard, the official minutes of the UK Parliament. Hansard is available online at https://hansard.parliament.uk/.

The core program is `mp_contrib.py` which scrapes contributions for a specific MP and produces a JSON file with a list of their contributions. This program is used manually to collect contributions for different MPs. One of the MPs must be Theresa May. The shell script `post_process.sh` is then used to check each of the files and create the composite outputs `all_contributions.json` and `other_contributions.json`. The "all" file contains all the MP inputs. The "other" file contains all MPs except Theresa May. These two files plus `theresa_may_contributions.json` form the output which can be used to train a neural network model.


Individual Programs
-------------------

##### `./mp_contrib.py <mp_name> [<list_start_page>]`
The MP name is searched for on Hansard. The supplied text is used as a search term so doesn't need to be the exact full name, just enough to uniquely identify the person.

The pages of contributions are then accessed one by one. Theresa May for instance has over 250 pages of contributions. Each page contains a summary of 20 contributions. For each contribution the program follows the link to the full contribution and collects the text.

The text is then tidied. Hansard question decoration is removed. Some regular expression substitutions are done to remove items in brackets, convert special characters to more normal punctuation, expand abbreviations and remove minimal contributions such as "rose" or "indicated dissent".

All the tidied contributions are put together in an output JSON file. The top level data structure of the JSON file is a list. Each element is a string with one contribution. Encoding is UTF-8. Contributions that consist of multiple paragraphs are divided by '\n'. 

##### `./check_chars.py <json_filename>`
This program makes sure a JSON contributions file only contains alphanumeric characters and a subset of special characters. It also prints a summary of the number of contributions, words and characters.

##### `./join.py <json_filename1> [<json_filename2>] ... <json_filename_out>`
This program joins a number of JSON contributions files to make one larger contribution file. For instance to collect together contributions from a group of MPs.
