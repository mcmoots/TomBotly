import yaml
import twitter
import random
import sys
import swifties
from wordnik import *
import logging
import socket
from time import sleep


class BotSwifty:

    def __init__(self, rootdir):

        self.last_tweet_file = rootdir + "last_tweet.txt"

        confs = yaml.load(open(rootdir + 'config.yaml'))
        self.api = twitter.Api(**confs['twitter_tokens'])

        wordnik_url = 'http://api.wordnik.com/v4'
        wordnik_key = confs['wordnik_key']
        self.client = swagger.ApiClient(wordnik_key, wordnik_url)
        self.wordnik = WordApi.WordApi(self.client)
        swifties.wordnik = self.wordnik

    def run_bot(self):

        # Follow/unfollow
        # Omit protected users from "followers" list to avoid issuing follow requests
        followers = set([fol.id for fol in self.api.GetFollowers() if fol.protected == False ])
        following = set([fol.id for fol in self.api.GetFriends()])

        to_follow = followers - following   # followers who are not yet followed
        to_unfollow = following - followers  # users who are no longer following back

        for follow in to_follow:
            self.api.CreateFriendship(user_id=follow)

        for unfollow in to_unfollow:
            self.api.DestroyFriendship(user_id=unfollow)

        # read in the last seen tweet
        f = open(self.last_tweet_file, "r")
        last_tweet = f.read()
        f.close()

        # Pull tweets from bot's home timeline
        tweets_full = self.api.GetHomeTimeline(exclude_replies=True, since_id=last_tweet)
        tweets = [tweet for tweet in tweets_full if tweet.retweeted_status is None]

        if len(tweets) == 0:
            sys.exit()

        authors = set([tweet.user.screen_name for tweet in tweets])

        tries = 0
        while tries < 4:
            author = random.sample(authors, 1)[0]
            tweet = random.choice([tweet for tweet in tweets if tweet.user.screen_name == author])

            s = swifties.Swifties(rootdir)
            reply_text = s.makeSwifty(tweet)
            if None == reply_text:
                tries += 1
                continue

            try:
                self.api.PostUpdate(reply_text, in_reply_to_status_id=tweet.id)
                break
            except twitter.TwitterError:
                tries += 1

        #store most recently seen tweet id
        f = open(self.last_tweet_file, "w")
        f.write(tweets_full[0].id_str)
        f.close()

        return True


if __name__ == '__main__':
    lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    lock_id = "mcmoots.botswifty"
    try:
        lock_socket.bind('\0' + lock_id)
        logging.debug("Got lock %r" % (lock_id,))
    except socket.error:
        # socket already locked, task must be running
        logging.info("Failed to get lock %r" % (lock_id,))
        sys.exit()

    if len(sys.argv) > 1:
        rootdir = sys.argv[1]
    else:
        rootdir = './'

    b = BotSwifty(rootdir)

    while True:
        b.run_bot()
        sleep(random.randrange(9999,11111))