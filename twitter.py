from tweepy import API
from tweepy import Cursor
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

import credentials

class Twitter_Streamer():
    # Class for streaming and processing live streams.
    def __init__(self):
        pass

    def stream_tweets(self, json_filename, hash_list):
        # This handles Twitter authentication and the connection to Twitter API.
        listener = StdOutListener()
        auth = OAuthHandler(credentials.CONSUMER_KEY, credentials.CONSUMER_SECRET)
        auth.set_access_token(credentials.API_KEY, credentials.API_SECRET)

        stream = Stream(auth, listener)
        stream.filter(track=hash_list)


class StdOutListener(StreamListener):
    # Standard listener class that prints recieved tweets to StdOut.

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
        print(status_code)

if __name__ == "__main__":

    hash_list = ['Donald Trump', 'Hillary Clinton', 'Barack Obama', 'Bernie Sanders']
    json_filename = "tweets.json"

    twitter_streamer = Twitter_Streamer()
    twitter_streamer.stream_tweets(json_filename, hash_list)