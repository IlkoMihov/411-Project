import json
import tweepy
import random
# Twitter API credentials
consumer_key = "FSYI0zkB071Ry7XDh1H6vnout"
consumer_secret = "PYybNMYCabLM1xySQMsuhwvdY3nLaMBzGumgfXZCAjw4kpjy1V"
access_key = "734984182288384001-7TodXT4R3PwOaCDG2kajlZjrLYNtbZW"
access_secret = "W7AnyHp0e8RoomuFrMxSO7xafFziLMf0XCuWwzBnxjt0r"

class getTweet():
    def __init__(self, user):
        self.user = user


    def search(self):
        # authorize twitter and initialize tweepy
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_key, access_secret)
        api = tweepy.API(auth)

        # load tweets
        status = api.user_timeline(screen_name=self.user, count=200)
        status = [json.dumps(entry._json) for entry in status]
        load_tweets = [json.loads(entry) for entry in status]

        # filter tweets
        get_tweets = [t['text'] for t in load_tweets]
        # do not include tweets with an image, retweets, or replies
        filter_tweets = [t for t in get_tweets if 'https://' not in t and 'RT' not in t and '@' not in t]
        # return random tweet
        return random.choice(filter_tweets)


