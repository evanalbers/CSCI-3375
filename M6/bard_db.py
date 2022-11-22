
import numpy as np
import pronouncing as p
import nltk
from nltk.corpus import brown
import requests
import bard as b
import json
from os.path import exists
from nltk.stem.lancaster import LancasterStemmer
from nltk.tokenize import word_tokenize
import string

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

"""trying to see if this is issue, populates lexicon from human limericks"""
def popTermFromHuman():

    global TERMINAL_MAP
    global TAG_LIST

    if exists("human_term_map.json"):
        with open("human_term_map.json", "r") as f:
            TERMINAL_MAP = json.load(f)
            TAG_LIST = list(TERMINAL_MAP.keys())
            print(TAG_LIST)
        return

    #will be resetting
    TAG_LIST = []

    human_lims = []

    with open("limerick_dataset_oedilf_v3.json", "r") as f:
        lims = json.load(f)

    for entry in lims:
        if entry['is_limerick']:
            human_lims.append(entry['limerick'])

 
    for lim in human_lims:
        lines = lim.split('\n')
        for line in lines:
            tokens = word_tokenize(line)
            token_tags = nltk.pos_tag(tokens)
            for t in token_tags: 

                if t[1] in TERMINAL_MAP and t[0] not in TERMINAL_MAP[t[1]]:
                    print(t[0])
                    TERMINAL_MAP[t[1]].append(t[0])
                elif t[1] not in TERMINAL_MAP:
                    print(t[0])
                    TERMINAL_MAP[t[1]] = []
                    TERMINAL_MAP[t[1]].append(t[0])
                    TAG_LIST.append(t[1])
    
    with open("human_term_map.json", "w") as f:
        json.dump(TERMINAL_MAP, f)

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

def add_human_lim(filename):

    human_lims = []

    mega_dict = {}

    with open(filename, "r") as f:
        human_data = json.load(f)

        for entry in human_data:
            if entry['is_limerick']:
                human_lims.append(entry['limerick'])

    with open("lim_data.json", "r") as f:
        mega_dict = json.load(f)
    
    #print(human_lims)

    with open("lim_data.json", "w") as f:
        mega_dict['1'] = human_lims
        json.dump(mega_dict, f)



"""
Evan Albers, Sofia Hamby, Soule Toure
CSCI 3725
PQ4: Social Networks
11/18/22

This starter code enables our neural network training! 
Basic helper functions to organize the dialogue data 

"""



    
def get_raw_training_data(filename):
    """Open a JSON file and extract its data into a list of dictionaries.
    Parameters: 
        filename: 'dialogue_data.csv', which was given
    Returns:
        training_data: List of dictionaries of dialogue
    """

    with open(filename, "r") as f:
        training_data = []

        file_data = json.load(f)

        human = file_data['1']
        computer = file_data['0']

        for num in range(20):
            lim = human[num]
            lim = lim.lower()
            mini_d = {}
            mini_d['origin'] = '1'
            mini_d['limerick'] = lim 
            training_data.append(mini_d)

        for num in range(20):
            lim = computer[num]
            lim = lim.lower()
            mini_d = {}
            mini_d['origin'] = '0'
            mini_d['limerick'] = lim 
            training_data.append(mini_d)
    
    return training_data

def preprocess_words(words, stemmer):
    """Takes in list of words, stems each, and returns a no-duplicates \
        list.
    Parameters: 
        words: The full spoken words from the dialogue
        stemmer: Stems words 
    Returns:
        stemmed_words: The list of stemmed words
    """

    stemmed_words = []

    for word in words:

        for char in word:
            
            if char not in string.punctuation:
                stemmed_word = stemmer.stem(word)
                stemmed_words.append(stemmed_word)
    
    # Weird! This changes the training output!
    # stemmed_words = list(set(stemmed_words))
    stemmed_words = [i for n, i in enumerate(stemmed_words) \
        if i not in stemmed_words[:n]]
    
    return stemmed_words

def organize_raw_training_data(raw_training_data, stemmer):
    """Iterates through training_data list and gives modified list of \
        word stems, a list of people/classes, and list of documents.
        args: raw_training_data (list of dictionaries) stemmer (stemmer)
        returns: words (list), classes (list), documents (list of tuples)
        """
           
    words = []

    #list of actors, leave no duplicates
    classes = []

    #document tuple
    documents = []

    #for each line of data
    for data in raw_training_data:

        sentence_tokens = word_tokenize(data['limerick'])
        sentence_tokens = preprocess_words(sentence_tokens, stemmer)

        words += sentence_tokens

        #checks if a person is in 
        if data['origin'] in classes:
            
            #search for their entry in documents
            for docs in documents:
                
                #if we come across given actor's document, add tokens
                if docs[1] == data["origin"]:
                    classes.append(data['origin'])
                    documents.append((sentence_tokens, data['origin']))
                    break
        else: 

            #adding person to classes, then new document added to documents
            classes.append(data['origin'])
            documents.append((sentence_tokens, data['origin']))

    words = preprocess_words(words, stemmer)
    classes = list(set(classes))

    return words, classes, documents

def create_training_data(words, classes, documents):
    """ Takes in list and outputs training data for Neural Network
    args: words (list), classes (list), documents (list of tuples)
    returns: training_data (list of lists), output (list of lists)
     """
    
    training_data = []
    output = []

    #make a bag and classifier list for each document
    for doc in documents:

        class_signifier = []
        
        for cl in classes:
            
            if doc[1] == cl:
                class_signifier.append(1)
            
            else: 
                class_signifier.append(0)
        
        output.append(class_signifier)

        bag = []
        
        for word in words:
            if word in doc[0]:
                bag.append(1)
            else:
                bag.append(0)
        training_data.append(bag)
    
    return training_data, output

def sigmoid(z):
    """ representation of a sigmoid function """
    
    z = np.exp(-z)
    sig = 1/(1+z)

    return sig

def sigmoid_output_to_derivative(output):
    """Convert the sigmoid function's output to its derivative.
    args: output to be converted
    returns: derivative 
    
    """
    return output * (1-output)
    
