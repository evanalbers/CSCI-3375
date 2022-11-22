"""
AUTHOR: Evan Albers 
COURSE: CSCI 3375
DUE DATE: 17 November 2022
ASSIGNMENT: M6, Poetry Generator

bard.py generates a limerick, where the user's input is the
inspiring subject and their characteristic   

- potential features include:
    - poems thematically inspired by input
    - poem has a joke

"""
import numpy as np
import pronouncing as p
from nltk.corpus import wordnet as wn
import bard_db as db
import json
from nltk.stem.lancaster import LancasterStemmer
from nltk.tokenize import word_tokenize
import string
import bard_trainer as bt
import os
import gtts as tts
from playsound import playsound

MARKOV_MATRICIES = {}


#general structure of a sentence: SUBJECT + VERB + OBJECT
#goal for structure of limerick: 1st sentence is a description,
#body is random actions, last sentence is also description. 

#limerick meter is anapestic, two meterical feet in lines 3, 4, 3 in others.
# anapestic meterical foot is two short syllables, followed by one long stressed
# will want to find ones that rhyme. 

#perhaps process should be: generate sentence, check for anapest meter, 
#if changing anything, check for meaning, then iterate over rhyming, check anapest again


#can find things with a "caused by relation"
#and a "has a" relation



""" initializing all possible terms in the CFG to equal prob """
def initializeMarkovMatrices(key=0, filename="", givenMM={}):

    global MARKOV_MATRICIES

    if filename != "":
        with open(filename, "r") as f:
            MARKOV_MATRICES = json.load(f)[key]
        return

    if givenMM != {}:
        MARKOV_MATRICES = givenMM

    starting_values = []

    for num in range(len(db.TAG_LIST)):
        starting_values.append(1 / len(db.TAG_LIST))

    for num in range(len(db.TAG_LIST)):    
        MARKOV_MATRICIES[num] = starting_values


""" function to choose a terminal symbol from list of terminal symbols
    currently just chooses a random one, want to add concept net support for considering weights"""

def chooseTerminal(tag, rhyme_scheme, rhyme_word=False): 

    terminals = db.TERMINAL_MAP[tag][:]

    possible_words = []

    rhyming_words = []

    for term in terminals:
        possible_pronun = p.phones_for_word(term)
        for pronun in possible_pronun:
            if rhyme_scheme.endswith(p.stresses(pronun)) and term not in possible_words:
                possible_words.append((term, p.stresses(pronun)))

    if rhyme_word != False:
        for word in possible_words:
            if word[0] in p.rhymes(rhyme_word):
                rhyming_words.append(word)
        possible_words = rhyming_words

    if len(possible_words) == 0:
        return (False, False)

    index = np.random.choice(len(possible_words))
    
    choice = possible_words[index]

    return choice[0], rhyme_scheme[:len(rhyme_scheme) - len(choice[1])]


""" simplfying base case for generateLine recursion """
def glBaseCase(tag, num_feet, rhyme_word):

    if num_feet == 3:
        rhyme_scheme = '001001001'
    else: 
        rhyme_scheme = '001001'
        
    line, remaining = chooseTerminal(tag, rhyme_scheme, rhyme_word)

    return remaining, line

""" tidying up recursive operations for generateLine """
def glPostRecursion(remaining_meter, line, tag):

    if remaining_meter == "":
        return remaining_meter, line
    else:
        
        new_info = chooseTerminal(tag, remaining_meter)

        if not new_info[0]:
            return new_info

        new_line = new_info[0] + " "  + line

        new_remaining = new_info[1]

        return new_remaining, new_line

def readjustWeights(tag, tag_list, weights):

    add = weights[tag_list.index(tag)] / (len(weights)-1)

    weights.pop(tag_list.index(tag))

    for num in range(len(weights)):
        weights[num] += add

    extra = 1 - sum(weights)

    weights[np.random.choice(len(weights))] += extra
    
    tag_list.remove(tag)

    return weights, tag_list


""" markov descent parser that generates sentence with given stress scheme """    
def generateLine(tag, num_feet, syllables, rhyme=False):

    global MARKOV_MATRICIES

    tags = db.TAG_LIST[:]

    weights = MARKOV_MATRICIES[tags.index(tag)][:]

    index = np.random.choice(len(tags), p=weights)

    next_tag = tags[index]

    if syllables == 0:

        return glBaseCase(tag, num_feet, rhyme)

    else: 

        remaining_meter, line = generateLine(next_tag, num_feet, syllables-1, rhyme)

        while line == False:

            if len(weights) == len(db.TAG_LIST) - 1:

                return remaining_meter, line

            weights, tags = readjustWeights(next_tag, tags, weights)
            
            index = np.random.choice(len(tags), p=weights)
            next_tag = tags[index]

            remaining_meter, line = generateLine(next_tag, num_feet, syllables-1, rhyme)
        
        return glPostRecursion(remaining_meter, line, tag)

def genLimerick():

    line_one = generateLine(np.random.choice(db.TAG_LIST), 3, 9)[1]

    if line_one == False:
        return False

    #print(line_one)

    line_two = generateLine(np.random.choice(db.TAG_LIST), 3, 9, line_one.split()[-1])[1]

    if line_two == False:
        return False

    #print(line_two)

    line_three = generateLine(np.random.choice(db.TAG_LIST), 2, 6)[1]

    if line_three == False:
        return False

    #print(line_three)

    line_four = generateLine(np.random.choice(db.TAG_LIST), 2, 6, line_three.split()[-1])[1]

    if line_four == False:
        return False

    #print(line_four)

    line_five = generateLine(np.random.choice(db.TAG_LIST), 3, 9, line_one.split()[-1])[1]

    if line_five == False:
        return False
    
    #print(line_five)

    return line_one + '\n' + line_two + '\n' + line_three + '\n' + line_four + '\n' + line_five


"""A function that verifies that the given line has "feet" number of anapestic meters

- args: line, feet
    - line is a string that is a potential line for the limerick whose meter we need to check
    - feet is an int that should be either two or three within the context of this program,
      as limerick lines contain either 2 or 3 meterical feet.

- returns: a bool representing whether the given line has "feet" anapestic meterical feet.
"""
    

#GENERAL IDEA: bard generates its own CFG, with a series of POS as an input from Spacy 
#then optimize markov weights for each POS, until we have a grammar it's happy with bassed on the classifier 



""" used to save some given text to json file"""
def saveToFile(lim_list):

    with open("lim_data.json", 'r') as f:

        mega_dict = json.load(f)
    

    mega_dict['0'] = lim_list

    with open("lim_data.json", 'w') as f:
        json.dump(mega_dict, f)

""" used to generate n limericks from bard"""
def genData(n, givenMM=''):

    if givenMM != '':
        MARKOV_MATRICIES = givenMM
    
    lim_list = []

    for num in range(n):
        print("LIMERICK #" + str(num))
        lim = genLimerick()
        if lim != False:
            lim_list.append(lim)
    
    saveToFile(lim_list)


""" train the model on some given fileset """
def trainModel(filename): 

    stemmer = LancasterStemmer()

    raw = db.get_raw_training_data("lim_data.json")
    words, classes, documents = db.organize_raw_training_data(raw, stemmer)
    training_data, output = db.create_training_data(words, classes, documents)

    # Comment this out if you have already trained once and don't want to re-train.
    bt.start_training(words, classes, training_data, output)

"""bard demo function"""

def bard_demo():
    with open("survivors.json", 'r') as f:
        survivors = json.load(f)
    top = max(list(survivors.keys()))
    bestMM = survivors[top]

    initializeMarkovMatrices(givenMM=bestMM)

    with open("demo_lims.json", "r") as f:
        lims = json.load(f)

    new_lim = genLimerick()

    spch = tts.gTTS(text=new_lim, lang='en')
    spch.save("demo.mp3")
    playsound("demo.mp3")
    
    print(new_lim)

    if '0' not in lims:
        lims['0'] = []
        
    lims['0'].append(new_lim)

    with open("demo_lims.json", "w") as f:
        json.dump(lims, f)





def main():

    db.popTermFromHuman()

    bard_demo()

    #print(lim)
    
    return 0


if __name__ == "__main__":
    main()



