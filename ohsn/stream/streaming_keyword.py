# -*- coding: utf-8 -*-
"""
Created on Wed Jun 03 03:43:09 2015

@author: wt

crawl stream with keyword-filtering
Keywords are in keywords.txt
https://dev.twitter.com/streaming/reference/post/statuses/filter
The track, follow, and locations fields should be considered to be combined with an OR operator.
track=foo&follow=1234 returns Tweets matching “foo” OR created by user 1234.

The United Kingdom lies between latitudes 49° to 61° N, and longitudes 9° W to 2° E.

Filter tweets with location, but few tweets have location information
Identify the location of users that post the crawled tweets, only store the users in UK
"""

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from twython import TwythonStreamer
import urllib
import imghdr
import os
import ConfigParser
import datetime
import ohsn.api.profiles_check as check
from ohsn.util import db_util as dbutil

config = ConfigParser.ConfigParser()
config.read(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)), 'conf', 'TwitterAPI.cfg'))

# spin up twitter api
APP_KEY = config.get('credentials3', 'app_key')
APP_SECRET = config.get('credentials3', 'app_secret')
OAUTH_TOKEN = config.get('credentials3', 'oath_token')
OAUTH_TOKEN_SECRET = config.get('credentials3', 'oath_token_secret')
print('loaded configuation')

# spin up database
DBNAME = 'young'
COLLECTION = 'stream'
db = dbutil.db_connect_no_auth(DBNAME)
tweets = db[COLLECTION]
user_set = set()
count = 0

# location_name = ['uk', 'u.k.', 'united kingdom', 'britain', 'england']

print("twitter connection and database connection configured")


class MyStreamer(TwythonStreamer):
    def on_success(self, data):
        if 'warning' in data:
            print (data['warning']['code'] + "\t" + data['warning']['message'] + "\t percent_full=" + data['warning']['percent_full'] +"\n")
        if 'text' in data:
            store_tweet(data)
            # print data['user']['screen_name'].encode('utf-8') + "\t" + data['text'].encode('utf-8').replace('\n', ' ')

    def on_error(self, status_code, data):
        print status_code
        print (data['warning']['code'] + "\t" + data['warning']['message'] + "\t percent_full=" + data['warning']['percent_full'] +"\n")

        # Want to stop trying to get data because of the error?
        # Uncomment the next line!
        # self.disconnect()


def get_pictures(tweet):
        # Get pictures in the tweets store as date-tweet-id-username.ext
        try:
            for item in tweet['entities']['media']:
                print item['media_url_https']
                if item['type']=='photo':
                    # print "PHOTO!!!"
                    urllib.urlretrieve(item['media_url_https'], 'api-timelines-scraper-media/' + item['id_str'])
                    # code to get the extension....
                    ext = imghdr.what('api-timelines-scraper-media/' + item['id_str'])
                    os.rename('api-timelines-scraper-media/' + item['id_str'], 'api-timelines-scraper-media/' + item['id_str'] + "." + ext)
        except:
            pass


def store_tweet(tweet, collection=tweets, pictures=False):
    """
    Simple wrapper to facilitate persisting tweets. Right now, the only
    pre-processing accomplished is coercing date values to datetime.
    """
    # print tweet
    global count
    print count+1
    count += 1
    if check.check_yg(tweet['user']) and tweet['user']['id'] not in user_set:
        user_set.add(tweet['user']['id'])
        tweet['created_at'] = datetime.datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
        collection.insert(tweet)
        # global location_name
        # user = tweet.get('user', None)
        # if user:
        #     location = user['location']
        #     if location:
        #         location = location.lower()
        #         if any(x in location for x in location_name):
        #             print location
        #             tweet['created_at'] = datetime.datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
        #             tweet['user']['created_at'] = datetime.datetime.strptime(tweet['user']['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
        #             # get pictures in tweet...
        #             if pictures:
        #                 get_pictures(tweet)
        #
        #             #print "TODO: alter the schema of the tweet to match the edge network spec from the network miner..."
        #             #print "TODO: make the tweet id a unique index to avoid duplicates... db.collection.createIndex( { a: 1 }, { unique: true } )"
        #             collection.insert(tweet)



while True:
    try:
        stream = MyStreamer(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
        # https://dev.twitter.com/streaming/overview/request-parameters                                 
        # stream.statuses.filter(language=['en'], track=['bulimic, anorexic, ednos, ed-nos, bulimia, anorexia, eating disorder, eating-disorder, eating disordered, eating-disordered, CW, UGW, GW2, GW1, GW'])
        track_list = []
        with open(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)), 'conf', 'keyword.txt')) as fo:
            for line in fo.readlines():
                track_list.append(line.strip())
        stream.statuses.filter(language=['en'], track=','.join(track_list))
    except Exception as detail:
        print str(detail)
