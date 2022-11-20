
import numpy as np
import pronouncing as p
import nltk
from nltk.corpus import brown
import requests
import bard as b
import json
from os.path import exists

TAG_LIST = ['ADJ', 'ADP', 'PUNCT', 'ADV', 'AUX',
            'SYM', 'INTJ', 'CCONJ','X', 'NOUN',
            'DET', 'PROPN', 'NUM', 'VERB', 'PART',	
            'PRON', 'SCONJ']

TERMINAL_MAP = {}




""" used to traverse concept net and populate a list of words related to the one submitted """
def CNtraverse(word, num):

    if num == 0:
        return []

    word_data = requests.get('http://api.conceptnet.io/c/en/' + word).json()

    related_words = []

    for e in word_data['edges']:
        related_words.append(e['end']['label'])
        related_words += CNtraverse(e['end']['label'], num-1)
    
    return related_words

def trimConceptNetData(words):

    split_words = []
    to_remove = []

    for w in words:
        parts = w.split()
        #print((parts, len(parts)))
        if len(parts) > 1:
            to_remove.append(w)
            for p in parts:
                split_words.append(p)
    
    for w in to_remove:
        words.remove(w)

    words += split_words

    return list(set(words))

def populateTerminalSymbols():

    global TERMINAL_MAP
    global TAG_LIST

    if exists("term_map.json"):
        with open("term_map.json", "r") as f:
            TERMINAL_MAP = json.load(f)
            TAG_LIST = list(TERMINAL_MAP.keys())
            print(TAG_LIST)
        return
    
    brown_corpus_tagged = brown.tagged_words(tagset='universal')

    for tag in TAG_LIST:
        TERMINAL_MAP[tag] = []
    
    for word in brown_corpus_tagged:

        if word[1] in TAG_LIST and word[0] not in TERMINAL_MAP[word[1]]:

            TERMINAL_MAP[word[1]].append(word[0])

    empty = [tag for tag in TERMINAL_MAP if len(TERMINAL_MAP[tag]) == 0]

    for tag in empty:

        TERMINAL_MAP.pop(tag)
        TAG_LIST.remove(tag)

    with open("term_map.json", "w") as f:
        json.dump(TERMINAL_MAP, f)


