#########################
# Streaming for @replies, hashtags and other shit.
# Me remixed
# For: IAMD 2017
########################

from twython import Twython, TwythonError
from twython import TwythonStreamer
import os
import re

CONSUMER_KEY = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
ACCESS_TOKEN_SECRET = os.environ['ACCESS_TOKEN_SECRET']
twitter = Twython(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
twitter.verify_credentials()

class meStreamer(TwythonStreamer):

	def on_success(self, data):
		if 'text' in data:
			acct = os.environ['MAIN_ACCOUNT']
			
			username = str(data['user']['screen_name'])
			body = str(data['text'])

			## only respond if you are directly tweeted at
			if body.startswith(acct):
				bodyStrip = re.sub(r'[^\w\s]','',body.lower())
				print("@%s: %s" % (username, bodyStrip))
				## grab the last tweet you tweeted, and turn it backwards, then re-tweet it back. 
				bodySend = bodyStrip.replace("n_remixed","")
				toTweet = "@{0} {1}".format(username,bodySend[::-1])
				try:
					twitter.update_status(status=toTweet)
					print("!sent: ",toTweet)
				except TwythonError as e:
					print(e)
					
meStream = meStreamer(CONSUMER_KEY,CONSUMER_SECRET,ACCESS_TOKEN,ACCESS_TOKEN_SECRET)
meStream.statuses.filter(track=os.environ['MAIN_ACCOUNT']) #only works if you are public