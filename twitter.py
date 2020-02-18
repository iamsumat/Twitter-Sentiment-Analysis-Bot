from tweepy import API
from tweepy import Cursor
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

from textblob import TextBlob

import credentials
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re


class TwitterClient:  # TWITTER CLIENT
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


class Twitter_Authenticator:  # TWITTER AUTHENTICATOR
    """
        Class for authenticating Twitter app.
    """

    def authenticate_app(self):
        auth = OAuthHandler(credentials.CONSUMER_KEY, credentials.CONSUMER_SECRET)
        auth.set_access_token(credentials.API_KEY, credentials.API_SECRET)
        return auth


class TwitterStreamer:  # TWITTER STREAMER
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
        # Overrides method in StreamListener Class

        try:
            print(raw_data)
            with open(self.json_filename, 'a') as tf:
                tf.write(raw_data)
            return True
        except BaseException as e:
            print("Error on data: %s" % str(e))

    def on_error(self, status_code):
        # Overrides method in StreamListener Class

        if status_code == 420:  # Returning False on_data method in case Twitter rate limit occurs.
            return False
        print(status_code)


class TweetAnalyzer:
    """
    Functionality for analyzing and categorizing content from tweets.
    """

    def clean_tweet(self, tweet):
        # Cleaning the tweet of all non-useful characters and words including emails, etc
        return ' '.join(re.sub(r"(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def analyze_sentiment(self, tweet):
        # Perform sentiment analysis with TextBlob and return out based on polarity
        analysis = TextBlob(self.clean_tweet(tweet))

        if analysis.sentiment.polarity > 0:
            return 1
        elif analysis.sentiment.polarity == 0:
            return 0
        else:
            return -1

    def tweets_to_df(self, tweets):
        # Initialize df and loop through all tweet data for every column

        df = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['tweets'])
        df['id'] = np.array([tweet.id for tweet in tweets])
        df['len'] = np.array([len(tweet.text) for tweet in tweets])
        df['date'] = np.array([tweet.created_at for tweet in tweets])
        df['source'] = np.array([tweet.source for tweet in tweets])
        df['retweets'] = np.array([tweet.retweet_count for tweet in tweets])
        df['likes'] = np.array([tweet.favorite_count for tweet in tweets])
        return df


if __name__ == "__main__":
    twitter_client = TwitterClient()
    tweet_analyzer = TweetAnalyzer()
    api = twitter_client.get_twitter_client_api()

    tweets = api.user_timeline(screen_name="BarackObama", count=200)  # user_timeline fn to set username and count

    tdf = tweet_analyzer.tweets_to_df(tweets)

    # Sentiment Analysis
    # Adding another column to the dataframe containing the sentiments
    tdf['sentiment'] = np.array([tweet_analyzer.analyze_sentiment(tweet) for tweet in tdf['tweets']])
    print(tdf[['tweets', 'sentiment']])
    print('*'*70)

    # Get average length of all tweets
    print("The average length of a tweet is %d characters/tweet." % (np.mean(tdf['len'])))

    # Get number of likes of the most liked tweet
    print("The most liked tweet has %d likes." % (np.max(tdf['likes'])))

    # Get most retweeted tweet
    print("The most retweets any tweet has had is %d retweets." % (np.max(tdf['retweets'])))

    # Time Series Analysis
    # Plotting 'likes' and 'retweets' against index date for 200 tweets
    time_likes = pd.Series(data=tdf['likes'].values, index=tdf['date'])
    time_likes.plot(figsize=(16, 4), label='Likes', legend=True)
    time_retweets = pd.Series(data=tdf['retweets'].values, index=tdf['date'])
    time_retweets.plot(figsize=(16, 4), label='Retweets', legend=True)
    plt.show()