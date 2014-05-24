import yaml
import twitter
import random
import sys
import swifties
from wordnik import *

if len(sys.argv) > 1:
    rootdir = sys.argv[1]
else:
    rootdir = './'


last_tweet_file = rootdir + "last_tweet.txt"

confs = yaml.load(open(rootdir + 'config.yaml'))
api = twitter.Api(**confs['twitter_tokens'])

wordnik_url = 'http://api.wordnik.com/v4'
wordnik_key = confs['wordnik_key']
client = swagger.ApiClient(wordnik_key, wordnik_url)
wordnik = WordApi.WordApi(client)
swifties.wordnik = wordnik

# Follow/unfollow

followers = set([fol.id for fol in api.GetFollowers()])
following = set([fol.id for fol in api.GetFriends()])

to_follow = followers - following   # followers who are not yet followed
to_unfollow = following - followers  # users who are no longer following back

for follow in to_follow:
    api.CreateFriendship(user_id=follow)

for unfollow in to_unfollow:
    api.DestroyFriendship(user_id=unfollow)

# read in the last seen tweet
f = open(last_tweet_file, "r")
last_tweet = f.read()
f.close()

# Pull tweets from bot's home timeline
tweets_full = api.GetHomeTimeline(exclude_replies=True, since_id=last_tweet)
tweets = [tweet for tweet in tweets_full if tweet.retweeted_status is None]

if len(tweets) == 0:
    sys.exit()

authors = set([tweet._user for tweet in tweets])

tries = 0
while tries < 4:
    author = random.sample(authors, 1)[0]
    tweet = random.choice([tweet for tweet in tweets if tweet._user == author])
    reply_text = swifties.pull_sentence_from_tweet(tweet)
    if None == reply_text:
        tries += 1
        continue

    try:
        api.PostUpdate(reply_text, in_reply_to_status_id=tweet.id)
        break
    except twitter.TwitterError:
        tries += 1


#store most recently seen tweet id
f = open(last_tweet_file, "w")
f.write(tweets_full[0].id_str)
f.close()