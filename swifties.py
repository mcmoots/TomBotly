# take a sentence, attempt to make a Tom Swifty pun

import random

from nltk.corpus import wordnet as wn

# set up stemmer
from nltk.stem.porter import *
stemmer = PorterStemmer()
import nltk.data
sentence_detector = nltk.data.load('tokenizers/punkt/english.pickle')

# load dictionary
sowpods = set(line.strip() for line in open('sowpods.txt'))
ends_in_ly = re.compile('ly$')
sowpodsly = filter(ends_in_ly.search, sowpods)

# WordNet stop list
# http://www.d.umn.edu/~tpederse/Group01/WordNet/wordnet-stoplist.html
wn_stops = ['i', 'a', 'an', 'as', 'at', 'by', 'he', 'his', 'me', 'or', 'thou', 'us', 'who']
wn_stops += ['are', 'out']

def find_ly_adverb(word):
    """Take a word and return an -ly adverb for it

    :rtype : basestring
    :param word:
    """
    wstem = stemmer.stem(word)
    # todo pull prefixes out into list for config section
    prefixes = '(un|out|in|up|pro|con|anti|pre|ante|en|non|re|a|co|ex|dis|de|mal|mis|over|under|post)'
    suffixes = '(ish|ous|eous|ful|l|il|i|ab|al|ib|less)'
    re_string = prefixes + '*' + wstem + suffixes + '*ly$'
    re_ly = re.compile(re_string)
    advs = filter(re_ly.match, sowpodsly)

    return advs


def find_syns(word, explain=False):
    'Take a word, traverse its wordnet synsets, check each lemma for an -ly adverb'
    if len(wn.synsets(word)) == 0:
        return []

    adverbs = []
    syns = []
    hyps = []
    ants = []
    # make a set of all lemma names, to speed up searching for adverbs
    # todo - write different rules for len(wn.synsets(word)) > 12. Polysemy returns too much obscure nonsense.
    for sset in wn.synsets(word):
        syns += [syn for syn in sset.lemma_names]
        for hyp in sset.hypernyms():
            hyps += [lemma for lemma in hyp.lemma_names]
        for l in sset.lemmas:
            ants += [a.name for a in l.antonyms()]

    jokes = set(syns + hyps + ants)

    if True == explain:
        syns = set(syns)
        hyps = set(hyps)
        ants = set(ants)
        print 'Synonyms: '
        print syns
        print 'Hypernyms: '
        print hyps
        print 'Antonyms: '
        print ants

    # TODO exclude syns that have the same stem as word

    for joke in jokes:
        adverbs += find_ly_adverb(joke)

    return adverbs

def swiftify_string(tweet, handle, maxlength):
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
        if len(word) > 2 and word.lower() not in wn_stops:
            adverbs += find_syns(word.lower(), False)

    if len(adverbs) == 0:
        return None

    # string: "tweet", said @handle adverbly.
    # length: tweet length + handle length + 12
    max_adv_length = maxlength - 13 - len(tweet) - len(handle)
    adverbly = random.choice([a for a in adverbs if len(a) <= max_adv_length])

    tweetstring = '"' + tweet + '", said @' + handle + ' ' + adverbly + '.'
    return tweetstring

#todo: rename this function
#todo: stop spitting out errors when swiftify_string returns a blank (replies = [None])
def pull_sentence_from_tweet(tweet):
    sentences = sentence_detector.tokenize(tweet.text)
    replies = []
    for s in sentences:
        # todo clean hashtags, urls, @-replies, etc
        replies.append( swiftify_string(s, tweet.user.screen_name, 140) )
    replies = filter(None, replies)
    if [None] != replies:
        return random.choice(replies)
    else:
        return None