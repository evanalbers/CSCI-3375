import numpy as np
import nltk
import json
from os.path import exists
from nltk.tokenize import word_tokenize
import string
import bard as b

TAG_LIST = []

TERMINAL_MAP = {}

def genData(n, givenMM): 
    """ used to generate n limericks from bard, save them to lim_data.json
    
    Parameters
    --------
    n : int
        number of limericks we want some MM to generate

    givenMM : dict
        a MM we want to use to generate the n limericks

    Returns
    --------
    None
    """

    
    lim_list = []

    num = 0

    #generate a limerick, add to lim_list
    while num < n:
        print(TAG_LIST)
        lim = b.genLimerick(givenMM)
        if lim != False:
            lim_list.append(lim)
            num += 1
    
    with open("Training Data/bard_lims.json", "w") as f:
        lim_dict = {}
        lim_dict["0"] = lim_list
        json.dump(lim_dict, f)


def getHumanLims():
    """gets a list of human limericks from default dataset 
    
    Parameters
    --------
    None

    Returns
    --------
    human_lims : list
        list of human written limericks

    Notes
    --------
    Only used for default data set, other datasets might take other forms
    so it is not a general function
    """

    human_lims = []

    #load human written lim data set
    with open("Training Data/limerick_dataset_oedilf_v3.json", "r") as f:
        lims = json.load(f)

    #contains some non-lim text, don't want those, get only the limericks
    for entry in lims:
        if entry['is_limerick']:
            human_lims.append(entry['limerick'])


    return human_lims

def populateTermMap(corpus, corpus_name):
    """ populates the TERMINAL_MAP from a given corpus
    
    Parameters
    --------
    corpus : list
        a list of strings that represents the chosen text corpus

    Returns
    --------
    None

    Notes
    --------
    Corpus must be a list of strings. This can be sentences or paragraphs
    """

    #for each entry in corpus
    for text in corpus:
        lines = text.split('\n')

        #for each line, tokenize, get pos tag
        for line in lines:
            tokens = word_tokenize(line)
            token_tags = nltk.pos_tag(tokens)

            #for each tag, check if already in TMap, if not, add it
            for t in token_tags: 
                if t[1] in TERMINAL_MAP and t[0] not in TERMINAL_MAP[t[1]]:
                    print(t[0])
                    TERMINAL_MAP[t[1]].append(t[0])
                elif t[1] not in TERMINAL_MAP:
                    print(t[0])
                    TERMINAL_MAP[t[1]] = []
                    TERMINAL_MAP[t[1]].append(t[0])
                    TAG_LIST.append(t[1])
    
    #save to file
    with open("Terminal Map/" + corpus_name, "w") as f:
        json.dump(TERMINAL_MAP, f)
    

def popTermFromHuman():
    """populates terminal map from human limerick database
    
    Parameters
    --------
    None

    Returns
    --------
    None

    Notes
    --------
    Uses the human limerick dataset as the corpus for terminal symbols, added
    because the classifier operates on word matching to a certain extent, so 
    simply having different words can make it difficult to fool the trainer. 
    """

    global TERMINAL_MAP
    global TAG_LIST

    #if it already exists, use it to avoid long load time
    if exists("Terminal Maps/default.json"):
        with open("Terminal Maps/default.json", "r") as f:
            TERMINAL_MAP = json.load(f)

            #only initialize if it isn't empty, otherwise should populate it
            if TERMINAL_MAP != {}:
                TAG_LIST = list(TERMINAL_MAP.keys())
                print(TAG_LIST)
                return

    human_lims = getHumanLims()

    populateTermMap(human_lims)

def assemble_default_human_lims():

    human_lims = getHumanLims()

    human_dict = {}

    human_dict["1"] = human_lims

    with open("Training Data/human_lims.json", "w") as f:
        json.dump(human_dict, f)


def get_raw_training_data():
    """Open a JSON file and extract its data into a list of dictionaries.
    Parameters: 
        filename: 'dialogue_data.csv', which was given
    Returns:
        training_data: List of dictionaries of dialogue
    """

    human = []
    computer = []

    with open("Training Data/human_lims.json", "r") as f:
        human = json.load(f)['1']    
    
    with open("Training Data/bard_lims.json", "r") as f:
        computer = json.load(f)['0']

    training_data = []

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
    """ Takes in list of words, stems each, and returns a no-duplicates list.
    Parameters
    --------
        words : list
            all words in the data
        stemmer : stemmer
            stems words

    Returns
    --------
        stemmed_words : list
            The list of stemmed words
    """

    stemmed_words = []

    for word in words:

        for char in word:
            
            if char not in string.punctuation:
                stemmed_word = stemmer.stem(word)
                stemmed_words.append(stemmed_word)
    
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

    #will be 0 or 1, 0 if computer, 1 if human
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
    
