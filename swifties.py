# take a sentence, attempt to make a Tom Swifty pun

import random
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn
from nltk.stem.porter import *
import nltk.data

class Swifties:
    def __init__(self, rootdir):
        # set up stemmer
        self.stemmer = PorterStemmer()
        self.sentence_detector = nltk.data.load('tokenizers/punkt/english.pickle')

        self.stops = stopwords.words('english')
        self.stops += ['are', 'out', 'guy', 'was', 'so', 'is', 'in', 'do', 'thou']

        sowpods = set(line.strip() for line in open(rootdir + 'sowpods.txt'))
        ends_in_ly = re.compile('ly$')
        self.sowpodsly = filter(ends_in_ly.search, sowpods)


    def findLy(self, word):
        """Take a word and return an -ly adverb for it

        :rtype : basestring
        :param word:
        """
        wstem = self.stemmer.stem(word)
        # todo pull prefixes out into list for config section
        prefixes = '(un|out|in|up|pro|con|anti|pre|ante|en|non|re|a|co|ex|dis|de|mal|mis|over|under|post)'
        suffixes = '(ish|ous|eous|ful|l|il|i|ab|al|ib|less)'
        re_string = prefixes + '*' + wstem + suffixes + '*ly$'
        re_ly = re.compile(re_string)
        advs = filter(re_ly.match, self.sowpodsly)

        return advs


    def findSyns(self, word, explain=False):
        'Take a word, get synonyms, check each for an -ly adverb'

        synos = wordnik.getRelatedWords(word, useCanonical=True, relationshipTypes='synonym')

        if synos == None:
            return []

        syns = synos[0].words
        adverbs = []

        for syn in syns:
            adverbs += self.findLy(syn)

        return adverbs


    def swiftifyString(self, tweet, handle, maxlength):
        """ Take a string + Twitter handle, build Swifty pun that stays within length limits

        Step 1: Generate list of all synonym-y adverbs for all words
        Step 2: Pick an adverb that stays within length limit
        Step 3: Assemble & return string
        """

        # split string into words - does NLTK have a better thing for this?
        words = [wn.morphy(word.lower()) for word in tweet.split()]
        words = [w for w in words if w is not None]
        adverbs = []

        # todo parse parts of speech, send only non-verbs/non-adverbs?
        for word in words:
            if len(word) > 2 and word.lower() not in self.stops:
                adverbs += self.findSyns(word.lower(), False)

        if len(adverbs) == 0:
            return None

        # string: "tweet", said @handle adverbly.
        # length: tweet length + handle length + 12
        max_adv_length = maxlength - 13 - len(tweet) - len(handle)
        adverbly = random.choice([a for a in adverbs if len(a) <= max_adv_length])

        tweetstring = '"' + tweet + '", said @' + handle + ' ' + adverbly + '.'
        return tweetstring


    def makeSwifty(self, tweet):
        sentences = self.sentence_detector.tokenize(tweet.text)
        replies = []
        for s in sentences:
            t = clean_tweet(s)
            replies.append( self.swiftifyString(t, tweet.user.screen_name, 140) )

        replies = filter(None, replies)

        if [None] != replies and len(replies) > 0:
            return random.choice(replies)
        else:
            return None


def clean_tweet(tweet):
    """ Strip URLs and hashtags
    :param tweet:
    :return:
    """
    urls = re.compile('https?:\/\/\S+', re.IGNORECASE)
    tweet = re.sub(urls, '', tweet)
    tweet = re.sub(r'#', '', tweet)
    return tweet