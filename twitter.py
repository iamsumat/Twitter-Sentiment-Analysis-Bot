from tweepy import API
from tweepy import Cursor
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

import credentials
import numpy as np
import pandas as pd


class TwitterClient():  # TWITTER CLIENT
    def __init__(self, twitter_user=None):
        self.auth = Twitter_Authenticator().authenticate_app()
        self.twitter_client = API(auth_handler = self.auth)
        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client

    def get_user_timeline_tweets(self, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets

    def get_friend_list(self, num_friends):
        friend_list = []
        for friend in Cursor(self.twitter_client.friends, id = self.twitter_user).items(num_friends):
            friend_list.append(friend)
        return friend_list

    def get_home_timeline_tweets(self, num_tweets):
        home_timeline_tweets = []
        for tweet in Cursor(self.twitter_client.home_timeline, id = self.twitter_user).items(num_tweets):
            home_timeline_tweets.append(tweet)
        return home_timeline_tweets


class Twitter_Authenticator(): # TWITTER AUTHENTICATOR
    '''
    Class for authenticating Twitter app.
    '''

    def authenticate_app(self):
        auth = OAuthHandler(credentials.CONSUMER_KEY, credentials.CONSUMER_SECRET)
        auth.set_access_token(credentials.API_KEY, credentials.API_SECRET)
        return auth


class TwitterStreamer():  # TWITTER STREAMER
    """
        Class for streaming and processing live streams.
    """

    def __init__(self):
        self.twitter_authenticate = Twitter_Authenticator()

    def stream_tweets(self, json_filename, hash_list):
        # This handles Twitter authentication and the connection to Twitter API.
        listener = TwitterListener(json_filename)
        auth = self.twitter_authenticate.authenticate_app()
        stream = Stream(auth, listener)
        stream.filter(track=hash_list)


class TwitterListener(StreamListener): # TWITTER STREAM LISTENER
    """
        Standard listener class that prints received tweets to StdOut.
    """

    def __init__(self, json_filename):
        self.json_filename = json_filename

    def on_data(self, raw_data):
        try:
            print(raw_data)
            with open(self.json_filename, 'a') as tf:
                tf.write(raw_data)
            return True
        except BaseException as e:
            print("Error on data: %s" % str(e))

    def on_error(self, status_code):
        if status_code == 420: # Returning False on_data method in case Twitter rate limit occurs.
            return False
        print(status_code)


class TweetAnalyzer():
    """
    Functionality for analyzing and categorizing content from tweets.
    """

    def tweets_to_df(self, tweets):
        df = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['Tweets'])
        return df


if __name__ == "__main__":
    twitter_client = TwitterClient()
    tweet_analyzer = TweetAnalyzer()
    api = twitter_client.get_twitter_client_api()

    tweets = api.user_timeline(screen_name="ILLENIUMMUSIC", count=20)

    print(dir(tweets[0]))

    # df = tweet_analyzer.tweets_to_df(tweets)
    # print(df.head())
    # 56:36