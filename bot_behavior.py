import yaml
import twitter
import random
import swifties

twitter_tokens = yaml.load(open('config.yaml'))
api = twitter.Api(**twitter_tokens)

# Follow all following users

followers = set([fol.id for fol in api.GetFollowers()])
following = set([fol.id for fol in api.GetFriends()])

to_follow = followers - following   # followers who are not yet followed
to_unfollow = following - followers  # users who are no longer following back

for follow in to_follow:
    api.CreateFriendship(user_id=follow)

for unfollow in to_unfollow:
    api.DestroyFriendship(user_id=unfollow)

# read in the last seen tweet


# Pull tweets from bot's home timeline

tweets_full = api.GetHomeTimeline(exclude_replies=True)
tweets = [tweet for tweet in tweets_full if tweet.retweeted_status is None]
tweet = random.choice(tweets)

#todo: loop this - if it can't find something on first try, pick a different tweet
reply_text = swifties.pull_sentence_from_tweet(tweet)
api.PostUpdate(reply_text, in_reply_to_status_id=tweet.id)

#todo - store most recently seen tweet ID in a file

