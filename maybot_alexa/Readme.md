Maybot Alexa
============

An implementation of Maybot as a skill for Amazon Alexa. The skill is called "Political Theresa" rather than Maybot as skill names cannot be a single word.

Maybot completes sentences in the style of Theresa May's parliamentary spoken contributions.

The server can be run either on a user's local computer or on a cloud server, in AWS or elsewhere.


Installation
------------

1. `sudo pip install flask`
   `sudo pip install flask-ask`

2. Install ngrok using `sudo apt-get install ngrok` or download from https://ngrok.com/download and install locally 

3. Edit the ngrok command in `run.sh` according to how you are going to expose the fulfillment server. Choices are no subdomain option (a random ngrok URL that changes each time you start ngrok) or `-subdomain` (a well defined ngrok URL). The latter requires a paid-for ngrok plan

4. Create a project in the Alexa Skills Kit console https://developer.amazon.com/edw/home.html
   Under Interaction Model, create a custom slot type using INITIAL_WORDS_TYPE.txt, fill in the Intent Schema from intents.txt and Sample Utterances from utterances.txt
   
6. Make sure the skill Configuration -> Endpoint is set to the ngrok https URL

7. `./run.sh`


Example Conversation
--------------------

```
User:       Alexa, Open Political Theresa
Maybot:     Hi! I'm a neural network that completes a sentence in the style of Theresa May.
            What are the first few words of the sentence you'd like me to complete?
User:       Brexit means
Maybot:     brexit means brexit, we will not be able to negotiate the best possible deal
            for the uk. i thank my honourable friend for raising that issue.
```
Alternatively as a single query:
```
User:       Alexa, ask Political Theresa to complete Brexit means
Maybot:     brexit means brexit, we will not be able to negotiate the best possible deal
            for the uk. i thank my honourable friend for raising that issue.
```


Useful websites
---------------

https://developer.amazon.com/blogs/post/Tx14R0IYYGH3SKT/flask-ask-a-new-python-framework-for-rapid-alexa-skills-kit-development
http://flask-ask.readthedocs.io/en/latest/getting_started.html
https://ngrok.com/docs
https://developer.amazon.com/edw/home.html
