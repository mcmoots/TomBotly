import yaml
import twitter
import random
import swifties

last_tweet_file = "last_tweet.txt"

twitter_tokens = yaml.load(open('config.yaml'))
api = twitter.Api(**twitter_tokens)

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
tweet = random.choice(tweets)

#todo: loop this - if it can't find something on first try, pick a different tweet
reply_text = swifties.pull_sentence_from_tweet(tweet)
api.PostUpdate(reply_text, in_reply_to_status_id=tweet.id)

#store most recently seen tweet id
f = open(last_tweet_file, "w")
f.write(tweets_full[0].id_str)
f.close()