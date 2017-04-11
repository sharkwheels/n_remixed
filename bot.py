###############################
# Me remixed
# For: IAMD 2017
# Remixes my private timeline into a public twitter feed
# using a markov chain
# This only runs on a cron / scheduler 
# v1.0
# REFERENCES
# 	http://stackoverflow.com/questions/27094275/how-to-post-image-to-twitter-with-twython
# 	https://www.flickr.com/help/forum/en-us/72157637405229644/
# 	http://joequery.me/code/flickr-api-image-search-python/
#	http://www.craigaddyman.com/mining-all-tweets-with-python/
# 	http://www.programcreek.com/python/example/82392/twython.TwythonError
#	http://stackoverflow.com/questions/43302982/update-twitter-status-with-an-image-in-twython-keep-getting-api-errors/
# ToDo
#	try and fix spacing some issues in scentences
# done
#	work in @ replies (Streaming api?)
# 	make a psuedo randomizer for each time it runs to make it not run every hour
# 	make apsuedo randomizer for images?
#	pick a random start date in the twitter timeline to avoid too many like tweets
#	make a simple flask face for heroku
###############################
###############################
# Me remixed
# For: IAMD 2017
# Remixes my private timeline into a public twitter feed
# using a markov chain
# This only runs on a cron / scheduler 
# v1.0
# REFERENCES
# 	http://stackoverflow.com/questions/27094275/how-to-post-image-to-twitter-with-twython
# 	https://www.flickr.com/help/forum/en-us/72157637405229644/
# 	http://joequery.me/code/flickr-api-image-search-python/
#	http://www.craigaddyman.com/mining-all-tweets-with-python/
# 	http://www.programcreek.com/python/example/82392/twython.TwythonError
#	http://stackoverflow.com/questions/43302982/update-twitter-status-with-an-image-in-twython-keep-getting-api-errors/
# ToDo
#	try and fix spacing some issues in scentences
# done
#	work in @ replies (Streaming api?)
# 	make a psuedo randomizer for each time it runs to make it not run every hour
# 	make apsuedo randomizer for images?
#	pick a random start date in the twitter timeline to avoid too many like tweets
#	make a simple flask face for heroku
###############################

from __future__ import print_function
from twython import Twython, TwythonError
import flickrapi
import markovify
import os
import random
import re
import requests
from io import BytesIO
from random import choice
from tweetIds import *

def connect():
	CONSUMER_KEY = os.environ['CONSUMER_KEY']
	CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
	ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
	ACCESS_TOKEN_SECRET = os.environ['ACCESS_TOKEN_SECRET']
	twitter = Twython(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
	twitter.verify_credentials()
	return twitter

def getSourceTweets(twitter,max_id,user_from):
	### Get some source tweets from my actual twitter timeline
	print("!sourceTweets", twitter,max_id,user_from)
	sourceTweets = []
	try:
		data = twitter.get_user_timeline(screen_name=user_from,count=200,trim_user=True,exclude_replies=True,max_id=max_id)
		for tweet in data:
			body = tweet['text']
			if body.startswith("RT @"):
				pass
			else:
				bodyScrubbed = filterTweet(body)
				if len(bodyScrubbed) != 0:
					sourceTweets.append(bodyScrubbed)
	except TwythonError as e:
		print(e)
	return sourceTweets

def getLastTweet(twitter,main_account):
	### Get the last tweet on the n_remix timeline
	lastTweet = ''
	try:
		data = twitter.get_user_timeline(screen_name=main_account,count=1,trim_user=True,exclude_replies=True)
		for tweet in data:
			body = tweet['text']
			bodyScrubbed = filterTweet(body)
			if len(bodyScrubbed) != 0:
				lastTweet = bodyScrubbed
	except TwythonError as e:
		print(e)
	return lastTweet	

def filterTweet(body):
	### Filter your results and remove most of the weird shit
	body = re.sub(r'\b(RT|MT) .+','',body) #take out anything after RT or MT
	body = re.sub(r'(\#|@|(h\/t)|(http))\S+','',body) #Take out URLs, hashtags, hts, etc.
	body = re.sub(r'\n','', body) #take out new lines.
	body = re.sub(r'\"|\(|\)', '', body) #take out quotes.
	body = re.sub(r'\s+\(?(via|says)\s@\w+\)?', '', body) # remove attribution
	return body

def makeSentence(text):
	### Pass everything to the markov module
	print("!makeSentence: ",text)

	text_model = markovify.Text(text)
	status = text_model.make_sentence()
	print("!makeSentence",status)
	return status

def findAnImage(status):
	### Go find an image from my flickr feed

	## define a search term from the new scentence you created. 
	print("!findAnImage - status: ", status)
	words = status.lower()
	words = status.split()
	print("!findAnImage - words: ", words)

	notWords = ["the","of","it","that","us","you","me","my",
				"in","and","or","maybe","yes","no","but","however",
				"therefore","out","even","her","him","his","hers","they",
				"there","their","thus","this","when","go","a","be","because",
				"all","some","while","an","for","will","also","we","me","you","is",
				"i","with","was","just","as","by","its","it's","so","does","do",
				"go","stop","these","to","too","who","what","where","when","why","been",
				"any","from","has","had","if","at","whilst","can","may","one","could","would",
				"should","not","she","he","since","here","about","once","twice","are",
				"our","your","you're","other","most","less","more","were","we're","my","test","least",
				"which","them","about","such","into","seem","seemed","though","tho","on","off",
				"those","these","than","many","_eg_","up","have","upon","like","appears","same","does","none","_at","_he",
				"1","2","3","4","5","6","7","8","9","10"
				]
	
	scrubbedWords = [x for x in words if x not in notWords]
	print("!findAnImage - scrubbedWords: ",scrubbedWords)
	searchTerm = random.choice(scrubbedWords)
	print("!findAnImage: search: ",searchTerm)
	
	# OAuth shit
	FLICKR_KEY = os.environ['FLICKR_KEY']
	FLICKR_SECRET = os.environ['FLICKR_SECRET']
	flickr = flickrapi.FlickrAPI(FLICKR_KEY, FLICKR_SECRET,format='parsed-json')
	flickr.authenticate_via_browser(perms='read')

	# Find The Thing
	photosToChooseFrom = []
	extras='url_sq,url_t,url_s,url_q,url_m,url_n,url_z,url_c,url_l,url_o'
	results = flickr.photos.search(user_id='91761058@N00',text=searchTerm, per_page=5,extras=extras)
	photos = results['photos']['photo']

	## get the original photo. I think they should ALL have original sizes. I hope. ugh.
	for i in photos:
		url = i['url_o']
		print(url)
		photosToChooseFrom.append(url)	
	toOpen = random.choice(photosToChooseFrom)
	return toOpen
	
	

if __name__=="__main__":
	
	# psuedo-randomizer. It doesn't run on every invocation. This will use the date by default
	random.seed()
	guess = random.randint(0,2)
	photoGuess =  random.randint(0,2)
	url = ""
	USER_FROM = os.environ['USER_FROM']
	MAIN_ACCOUNT = os.environ['MAIN_ACCOUNT']

	# only run if the number is 0 
	if guess == 0:

		# connect to twitter
		twitter = connect()

		# getting max_id from a giant ass list to get 200 tweets from different places in timeline
		maxIdDataBase = maxIdList
		max_id = random.choice(maxIdDataBase)
		print(max_id)
		# connect to the twitter api
		
		# get the last tweet and make a source for the markov library
		lastTweet = getLastTweet(twitter,MAIN_ACCOUNT)
		sourceTweets = getSourceTweets(twitter,max_id,USER_FROM)
		#print("!main: ",sourceTweets)
		sourceText = " ".join(sourceTweets)
		#print("!main: ",sourceText)			#working
		
		# generate a scentence
		newScentence = makeSentence(sourceText)
		print("!main(newScentence): ",newScentence)
		print("!main(lastTweet): ", lastTweet)
		# if its time to go find an image...
		if photoGuess == 0:
			url = findAnImage(newScentence)	
		# make sure the new scentence isn't the same as the old sentece
		# else get a new one
		if newScentence != lastTweet:
			if url:
				response = requests.get(url)
				photo = BytesIO(response.content)
				response = twitter.upload_media(media=photo)
				twitter.update_status(status=newScentence, media_ids=[response['media_id']])
				print("!sent+image: ",newScentence,response)
				url = ""
			else:
				print("no photo at this time")
				twitter.update_status(status=newScentence)
				print("!sent: ",newScentence)
		else:
			newScentence = makeSentence(sourceText)
	else:
		print("not invoking this time")

