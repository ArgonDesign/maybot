Maybot Google
=============

An implementation of Maybot as an Action for Google Home/Assistant. The action is called "Political Theresa" rather than Maybot so it has a distinctive name using standard words that Google's speech recogniser catches reliably.

Maybot completes sentences in the style of Theresa May's parliamentary spoken contributions.

The action is implemented as a combination of an agent using API.AI and a fulfillment web server in Python using flask-assistant. The fulfillment server can be run either on a user's local computer or on a cloud server, in GCS or elsewhere.


Installation
------------

1. `sudo pip install flask`
   `sudo pip install flask-assistant`

2. Install ngrok using `sudo apt-get install ngrok` or download from https://ngrok.com/download and install locally

3. Edit the ngrok command in `run.sh` according to how you are going to expose the fulfillment server. Choices are no subdomain option (a random ngrok URL that changes each time you start ngrok) or `-subdomain` (a well defined ngrok URL). The latter requires a paid-for ngrok plan

4. Create a project on Actions on Google https://console.actions.google.com. Use `ActionsOnGoogle_Settings.txt` for help filling in fields

5. Create the agent on API.AI. Import from `Maybot.zip` or fill in fields manually using `API.AI_Settings.txt` as a guide
   
6. Make sure the URL in API.AI Fulfillment is set to the ngrok https URL 

7. `./run.sh`


Example Conversation
--------------------

Will work with English (US) or English (UK).

```
User:               OK Google, talk to Political Theresa
Google:             Sure. Here's Political Teresa.
                    ... Bong as agent starts
Political Theresa:  Hi! I'm a neural network that completes a sentence in the style of Theresa May. What
                    are the first few words of the sentence you'd like me to complete?
User:               Brexit means
Political Theresa:  brexit means brexit, we will not be able to negotiate the best possible deal for
                    the uk. i thank my honourable friend for raising that issue.
                    ... Bong as agent closes
```
Alternatively as a single query:
```
User:               OK Google, talk to Political Theresa about brexit
Google:             Sure. Here's Political Teresa.
                    ... Bong as agent starts
Political Theresa:  brexit is about the efficient use of resources. police and crime commissioners, as i
                    have said, will bring accountability to local policing.
                    ... Bong as agent closes
```


Useful websites
---------------

https://console.actions.google.com
https://console.api.ai/api-client/

https://docs.api.ai/docs
https://github.com/treethought/flask-assistant
