import time
import oauth2
from io import BytesIO
from PIL import Image
import urllib.request
import os
import keys
import tweepy
import mysql.connector

CONSUMER_KEY = keys.CONSUMER_KEY
CONSUMER_SECRET = keys.CONSUMER_SECRET
ACCESS_TOKEN = keys.ACCESS_TOKEN
ACCESS_SECRET = keys.ACCESS_SECRET


def searchDDBB(query, values):
	connection = mysql.connector.connect(user="andres", password=keys.PASSWORD_DDBB, host="127.0.0.1",
	                                     database="informerbot")
	cursor = connection.cursor()
	# query = "SELECT idMsg, text FROM messages"
	cursor.execute(query)
	for values in cursor:
		print(cursor)


def insertToDDBB(idMsg, text, type, idSender):
	connection = mysql.connector.connect(user="andres", password=keys.PASSWORD_DDBB, host="127.0.0.1",
	                                     database="informerbot")
	cursor = connection.cursor()
	add_message = ("INSERT INTO messages "
	               "(idMsg, text, type, idSender) "
	               "VALUES (%s, %s, %s, %s)")
	data_message = (idMsg, text, type, idSender)
	cursor.execute(add_message, data_message)
	connection.commit()
	cursor.close()
	connection.close()


def oauth_request(url, http, post="", headers=None):
	consumer = oauth2.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)
	token = oauth2.Token(key=ACCESS_TOKEN, secret=ACCESS_SECRET)
	client = oauth2.Client(consumer, token)
	resp, content = client.request(url, method=http, headers=None)
	return content


def publishImage(url, message):
	# Get authenticated to media url
	photo = oauth_request(url, "GET")
	file = BytesIO(photo)
	img = Image.open(file)
	img.save("img.jpg")
	# Publish image
	api.update_with_media("img.jpg", status=message)
	os.remove("img.jpg")

def publishVideo(url, message): #Tweepy publish video
	urllib.request.urlretrieve(url, "video.mp4")
	api.update_with_media("video.mp4", status=message)
	os.remove("video.mp4")
	

def publish(last_tweet, messages):
	if len(messages) > 0:
		messages_to_publish = []
		file = open("idLastTweet", "r")
		id = file.read()
		file.close()
		if last_tweet is not None:  # and last_tweet is msg[0].message_create['message_data']['text']:
			for i in messages:
				#if i.message_create['message_data']['text'] == last_tweet:
				if i.id == id:
					messages_to_publish = messages[0:(messages.index(i))][::-1]  # New list since the begin till the previous tweeted msg
					break
		else:
			messages_to_publish = messages[::-1]
		
		for i in messages_to_publish:
			if len(i.message_create['message_data']) == 2:  # Text
				text = i.message_create['message_data']['text']
				api.update_status(text)
				time.sleep(10)
			elif len(i.message_create['message_data']) == 3:  # Image or Video
				url = i.message_create['message_data']['attachment']['media']['media_url_https']
				message = i.message_create['message_data']['text']
				message = message[:message.find("https://")]
				print("JASJJASJASJ ",i.message_create['message_data']['attachment']['type'])
				if i.message_create['message_data']['attachment']['media']['type'] == "video":
					publishVideo(url, message)
				else:
					# i.destroy()
					publishImage(url, message)
			idMsg = i.id
			file = open("idLastTweet", 'w')
			file.write(idMsg)
			file.close()


auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
img = False
# insertToDDBB(4, "JAJA", "text", 12123)

while True:
	try:
		timeline = api.home_timeline(count=1)
		messages = api.list_direct_messages()
		last_tweet_text = ""
		if len(timeline) > 0:  # Check if there are published tweets
			counter = 2
			if timeline[0].text[8:12] != "t.co":
				last_tweet_text = timeline[0].text
			else:
				while last_tweet_text is None and last_tweet_text[8:12] == "t.co":
					timeline = api.home_timeline(count=counter)
					if len(timeline) > counter - 1:
						if timeline[counter - 1].text[8:12] != "t.co":
							last_tweet_text = timeline[counter - 1].text
					else:
						last_tweet_text = None
				print("Last Tweet published: ")
				print(last_tweet_text)
		else:
			last_tweet_text = None
		
		messages = api.list_direct_messages()
		messagesText = [msg.message_create['message_data']['text'] for msg in messages]
		print("Messages to publish")
		print(messagesText)
		publish(last_tweet_text, messages)  # TODO /[::-1] to reverse msg
		print("Sleeping 1'50 minutes")
		time.sleep(90)
	except tweepy.RateLimitError:
		print("Sleeping")
		time.sleep(5 * 60)
# TODO citas a tweets, stickers, fotos, videos, gifs, links, msg sin texto"""
