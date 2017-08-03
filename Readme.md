Maybot
======

Maybot is a deep neural network that completes sentences in the style of Theresa May's parliamentary spoken contributions.

There are implementations in subdirectories for the web (`maybot_web`), as a skill for Amazon Alexa (`maybot_alexa`) and as an action for Google Home/Assistant (`maybot_google`). The  Alexa and Google versions are called "Political Theresa" as the voice systems require a multi-word activation name.

These implementations use a common neural network model. The directory structure supports having multiple models, each as a subdirectory of the `models` directory. The `model` symlink points to the chosen model. Each model must provide a Python `create_sentence()` function, but can otherwise use whatever technology is desired.

The model provided, `models/sjb_word_model`, is written using Keras in Python. The model predicts the next word in a sentence from the preceding 12 words which are maintained in a shift register and presented to the model in parallel. The model has 4 dense layers with interspersed droput and ELU layers. [word2vec](https://radimrehurek.com/gensim/models/word2vec.html) is used to code words as 300-element vectors which form the input to the network. The output of the model has a probabalistic selector so that it can be adjusted by "temperature" to be more or less inventive.

The spoken contributions used for training have been obtained by scraping [Hansard Online](https://hansard.parliament.uk/), the official verbatim report of proceedings of both the House of Commons and the House of Lords.

`hansard_scrape` contains the code to scrape the spoken contributions and the data files that have been collected. The key output files are `all_contributions.json`, `other_contributions.json` and `theresa_may_contributions.json`. These are symlinked to by the models which use them as training data.

`images` contains the original images and the files created from them that are used by the different web/voice platform implementations.

`test.py` is a basic test program to quickly check that the model is working. It completes a sentence starting "The right honourable gentleman" and prints out the result.

`run.sh` starts `maybot_web`, `maybot_alexa`, `maybot_google` and `ngrok` in a tabbed gnome-terminal. The ngrok settings are contained in `ngrok.yml`. Edit this file according to how you are going to expose the servers.
