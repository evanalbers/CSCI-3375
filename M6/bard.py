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
import requests
import nltk
from nltk.corpus import wordnet as wn
import bard_db as db

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
def initializeMarkovMatrices():

    global MARKOV_MATRICIES

    starting_values = []

    for num in range(len(db.TAG_LIST)):
        starting_values.append(1 / len(db.TAG_LIST))

    for num in range(len(db.TAG_LIST)):    
        MARKOV_MATRICIES[num] = starting_values


""" function to choose a terminal symbol from list of terminal symbols
    currently just chooses a random one, want to add concept net support for considering weights"""

def chooseTerminal(tag, rhyme_scheme): 

    terminals = db.TERMINAL_MAP[tag]

    possible_words = []

    for term in terminals:
        possible_pronun = p.phones_for_word(term)
        for pronun in possible_pronun:
            if rhyme_scheme.endswith(p.stresses(pronun)) and term not in possible_words:
                possible_words.append((term, p.stresses(pronun)))
    
    index = np.random.choice(len(possible_words))
    
    choice = possible_words[index]

    return choice[0], rhyme_scheme[:len(rhyme_scheme) - len(choice[1])]


""" simplfying base case for generateLine recursion """
def glBaseCase(tag, num_feet):

    if num_feet == 3:
        rhyme_scheme = '001001001'
    else: 
        rhyme_scheme = '001001'
        
    line, remaining = chooseTerminal(tag, rhyme_scheme)

    return remaining, line

""" tidying up recursive operations for generateLine """
def glPostRecursion(remaining_meter, line, tag):

    if remaining_meter == "":
        return remaining_meter, line
    else:
    
        new_info = chooseTerminal(tag, remaining_meter)

        new_line = new_info[0] + " "  + line

        new_remaining = new_info[1]

        return new_remaining, new_line

""" markov descent parser that generates sentence with given stress scheme """    
def generateLine(tag, num_feet, syllables):

    global MARKOV_MATRICIES

    weights = MARKOV_MATRICIES[db.TAG_LIST.index(tag)]

    index = np.random.choice(len(db.TAG_LIST), p=weights)

    next_tag = db.TAG_LIST[index]

    print(next_tag)

    if syllables == 0:

        return glBaseCase(tag, num_feet)

    else: 

        remaining_meter, line = generateLine(next_tag, num_feet, syllables-1)
        
        return glPostRecursion(remaining_meter, line, tag)

def genLimerick():
    limerick = generateLine('NOUN', 3, 9)[1] + "\n" + \
               generateLine('NOUN', 3, 9)[1] + "\n" + \
               generateLine('NOUN', 2, 6)[1] + '\n' + \
               generateLine('NOUN', 2, 6)[1] + '\n' + \
               generateLine('NOUN', 3, 9)[1]

    return limerick









# """ Finding verbs related to the inspiring word """
# def findVerbs(word):
    
#     word_data = requests.get('http://api.conceptnet.io/c/en/' + word).json()

#     verb = []

#     for e in word_data['edges']:
#         if e['rel']['label'] == ("CapableOf" or "UsedFor" or "Causes"):
#             verb.append(e['end']['label'])

#     return verb



# """
# Find words related to a given word
# """
# def searchRelations(word):

#     word_data = requests.get('http://api.conceptnet.io/related/c/en/' + word + "?filter=/c/en").json()

#     potential_words = []

#     for related in word_data['related']:
#         potential_words.append(related["@id"][6:])
        

#     return potential_words

"""A function that verifies that the given line has "feet" number of anapestic meters

- args: line, feet
    - line is a string that is a potential line for the limerick whose meter we need to check
    - feet is an int that should be either two or three within the context of this program,
      as limerick lines contain either 2 or 3 meterical feet.

- returns: a bool representing whether the given line has "feet" anapestic meterical feet.
"""
    

#GENERAL IDEA: bard generates its own CFG, with a series of POS as an input from Spacy 
#then optimize markov weights for each POS, until we have a grammar it's happy with bassed on the classifier 
def getInspo():
    word = input("What would you like to hear about? : ")
    return word.strip().lower()

def saveToFile(text, title):

    with open(title + ".txt", 'w') as f:
        f.writelines(text)


def main():

    db.populateTerminalSymbols()

    print(db.TAG_LIST)

    initializeMarkovMatrices()

    remaining, line = generateLine('NOUN', 3, 9)

    print(line)

    print(genLimerick())
    return 0


if __name__ == "__main__":
    main()



