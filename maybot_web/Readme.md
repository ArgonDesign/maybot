Maybot Web
==========

Maybot is a web application that completes sentences in the style of Theresa May's parliamentary spoken contributions.

The application also provides a page URL/privacy with privacy and legal details. This URL can be given as the privacy policy for Actions on Google, which requires that you provide such information.


Installation
------------

1. `sudo pip install flask`

2. Install ngrok using `sudo apt-get install ngrok` or download from https://ngrok.com/download and install locally

3. Edit the ngrok command in `run.sh` according to how you are going to expose the website. Choices are no subdomain or hostname option (a random ngrok URL that changes each time you restart ngrok), `-subdomain` (a well defined ngrok URL) or `-hostname` (your own URL). The latter two require paid-for ngrok plans. `-hostname` requires the Pro plan or above

4. `./run.sh`


Useful websites
---------------

http://flask.pocoo.org/
https://ngrok.com/docs
