"""
AUTHOR: Evan Albers 
COURSE: CSCI 3375
DUE DATE: 22 November 2022
ASSIGNMENT: M6, Poetry Generator

bard.py generates a limerick with no input from the user. It contains the 
body of limerick generating code, including the basic framework of 
recursive limerick generation, as well as saving limericks to files,
and the demo code that generates a limerick using the top performing 
markov matrix, and plays it out loud for the user.

"""
import numpy as np
import pronouncing as p
import bard_db as db
import json
from nltk.stem.lancaster import LancasterStemmer
import bard_trainer as bt
import gtts as tts
import copy


MARKOV_MATRICIES = {}
RETRY = 1


def initializeMarkovMatrices(key=0, filename="", givenMM={}):
    """ initializing all probabilities in the markov martix (MM) 

    Parameters
    --------
    key : float, optional
        represents the average delta of some given MM, 
        MM are mapped to this value in the survivors.json file.

    filename : float, optional
        represents the filename of a file containing
        MM mapped to their average delta values, in all cases within this 
        program, this is survivors.json. However, if one wants to potentially
        use a different file, perhaps a MM generated on a different instance 
        of the program, this is possible.

    givenMM : dict, optional
        a MM that we want to set as the current MM, used when 

    Returns
    --------
    None

    Note: if nothing given, function simply sets all probabilities as equal
          (IE, P(tag) = 1/(number of tags))
 """

    global MARKOV_MATRICIES

    #if a filename has been given, grab the MM at given key as well from said file
    if filename != "":
        with open(filename, "r") as f:
            MARKOV_MATRICES = json.load(f)[key]
        return

    #if MM given, initialize to those values
    if givenMM != {}:
        MARKOV_MATRICES = copy.deepcopy(givenMM)
        print(MARKOV_MATRICES)
        return

    #otherwise, if none of the optional param are given, initialize all
    #values to equal
    starting_values = []

    for num in range(len(db.TAG_LIST)):
        starting_values.append(1 / len(db.TAG_LIST))

    for num in range(len(db.TAG_LIST)):    
        MARKOV_MATRICIES[num] = starting_values


def chooseTerminal(tag, rhyme_scheme, rhyme_word=False): 
    """ function to choose a terminal symbol from list of terminal symbols

    Parameters
    --------
    tag : string
        representing one of the parts of speech in db.TAG_LIST
        
    rhyme_scheme : string
        representing the "remaining" rhyme left when 
        the funtcion is being called. For example, if chooseTerminal were
        choosing the last word of the first line, rhyme_scheme would be 
        "001001001"

    rhyme_word : string, optional
        if there is a word we need to rhyme
        with, pass the word in as an arg, otherwise the default value is 
        false and we don't need to worry about it.

    Returns
    -------
    Choice[0] : string
        the chosen word

    remaining_rhyme : string
        is the remaining available rhyme_scheme.
        For example, if the chosen word is "Cat", and the rhyme_scheme 
        argument was originally "001001001", then remaining_rhyme will
        be "00100100"

    False Tuple : (False, False)
        In the event that a terminal symbol cannot be found
        (perhaps one doesn't rhyme, or doesn't fit rhyme scheme), then 
        return false, false. Other functions know how to handle this. 
    """

    #make a copy of terminal symbols
    terminals = db.TERMINAL_MAP[tag][:]

    possible_words = []

    rhyming_words = []

    #find stresses for each terminal symbol
    for term in terminals:
        possible_pronun = p.phones_for_word(term)

        #check each pronunciation, if it fits the rhyme scheme and the word
        #hasn't been added, add it
        for pronun in possible_pronun:
            if rhyme_scheme.endswith(p.stresses(pronun)) and \
                term not in possible_words:

                possible_words.append((term, p.stresses(pronun)))

    #if we do need the word to rhyme, iterate over possible words and 
    #check whether they rhyme with given words
    if rhyme_word != False:
        for word in possible_words:
            if word[0] in p.rhymes(rhyme_word):
                rhyming_words.append(word)
        
        #possible words is now only those that rhyme
        possible_words = rhyming_words

    #if there are no rhyming words, return False tuple
    if len(possible_words) == 0:
        return (False, False)

    #otherwise, choose a random word from list of possible words
    index = np.random.choice(len(possible_words))
    
    choice = possible_words[index]

    #then modify the rhyme scheme to reflect the choice
    remaining_rhyme = rhyme_scheme[:len(rhyme_scheme) - len(choice[1])]

    #return word and remaining rhyme scheme
    return choice[0], remaining_rhyme



def glBaseCase(tag, num_feet, rhyme_word):
    """ tidying up base case for generateLine recursion 
    
    Parameters
    --------
    tag : string
        the chosen tag for the call to chooseTerminal
    
    num_feet : int
        the number of anapestic metrical feet in the given line
    
    rhyme_word : string
        the word with which this terminal symbol should rhyme
        necessary because base case is the last word of the line

    Returns
    --------
    remaining : string 
        string representing the remaining meter in a line after adding
        the chosen terminal symbol (word).

    line : string
        the string representing the line generated thus far (at base
        case, this is simply the last word)
    """

    #if lines 1,2 or 5
    if num_feet == 3:
        rhyme_scheme = '001001001'
    else: 
        rhyme_scheme = '001001'
        
    line, remaining = chooseTerminal(tag, rhyme_scheme, rhyme_word)

    return remaining, line


def glPostRecursion(tag, remaining_meter, line):
    """ tidying up recursive operations for generateLine

    Parameters
    --------
    tag : string
        chosen tag for this call to chooseTerminal
        
    remaining_meter : string
        the remaining meter left in the line
        
    line : string
        the line generated so far by recursion

    Returns
    --------
    new_remaining : string
        a string representing the remaining rhyme scheme of the line
        after the new word is added
        
    new_line : string
        the new line after the new chosen word is added
    """

    #if there is no meter left, line is complete, just return that
    if remaining_meter == "":
        return remaining_meter, line
    else:
        
        #choose a new line
        new_info = chooseTerminal(tag, remaining_meter)

        #if we get (False, False) back, simply return that
        if not new_info[0]:
            return new_info

        new_line = new_info[0] + " "  + line

        new_remaining = new_info[1]

        #return updated rhyme_scheme, line
        return new_remaining, new_line

def readjustWeights(tag, tag_list, weights):
    """ removes a tag from list, readjusts weights accordingly 
    
    Parameters
    --------
    tag : string
        the tag that failed, needs to be removed from consideration
    
    tag_list : list
        list of all tags, from which tag is to be removed
    
    weights : list
        given entry for tag in the MM

    Returns
    --------
    weights : list
        readjusted weights, minus the removed tag's entry

    tag_list : list
        list of tags, minus the removed one
    """

    #amount that will be added to each other entry in this MM entry
    add = weights[tag_list.index(tag)] / (len(weights)-1)

    #remove given tag entry
    weights.pop(tag_list.index(tag))

    #add the fraction of the removed weights to each remaining entry
    for num in range(len(weights)):
        weights[num] += add

    #if they don't add up to one, add the discrepancy to a random entry
    extra = 1 - sum(weights)
    weights[np.random.choice(len(weights))] += extra

    #remove tag from tag_list
    tag_list.remove(tag)

    return weights, tag_list


def generateLine(givenMM, tag, num_feet, syllables, rhyme=False):
    """ markov descent parser that generates a line with given meter and stress

    Parameters
    --------
    givenMM : dict
        MM to generate limerick with

    tag : string
        chosen tag for this stage in the line

    num_feet : int
        number of anapestic metrical feet for this line

    syllables : int
        number of possible syllables left in the line

    rhyme : string, optional
        if given, the word with which the last word in the line should rhyme
    
    Returns
    --------
    new_remaining : string
        same as glPostRecursion, string representing the remaining meter
        will be "" on final return

    new_line : string
        again same as glPostRecursion, the line generated thus far by the call
    """ 

    print(givenMM)

    #make a copy of the tag list
    tags = db.TAG_LIST[:]
    print(tags)

    print(tag)
    #make a copy of the MM
    weights = givenMM[str(tags.index(tag))][:]

    #choose a tag according to the MM
    index = np.random.choice(len(tags), p=weights)
    next_tag = tags[index]
    print(tags)
    print(next_tag)

    #if no more syllables, we have reached the base case
    if syllables == 0:

        return glBaseCase(tag, num_feet, rhyme)

    else: 

        remaining_meter, line = generateLine(givenMM, next_tag, num_feet, 
                                            syllables-1, rhyme)
        #if chooseTerminal fails at some point, retry 
        while line == False:

            #this dictates how many times we retry, should be kept low, 
            #either one or zero
            if len(weights) == len(db.TAG_LIST) - RETRY:

                return remaining_meter, line

            #readjust weights if we want to try again, 
            #remove the tag that led to failure
            weights, tags = readjustWeights(next_tag, tags, weights)
            
            #choose a new one
            index = np.random.choice(len(tags), p=weights)
            next_tag = tags[index]

            remaining_meter, line = generateLine(givenMM, next_tag, num_feet, 
                                                syllables-1, rhyme)
        #run post recursion (ie, choosing terminal symbol, and other bits)
        #and return
        return glPostRecursion(tag, remaining_meter, line)

def genLimerick(givenMM):
    """ generates a limerick 
    
    Parameters
    --------
    givenMM : dict
        MM to generate limerick with

    Returns
    --------
    limerick : string
        a string representing the generated limerick

    Note: if any one of the lines completely fails, typically faster to just
    return false and ditch it, so that's what it does. Retrying is expensive
    """

    line_one = generateLine(givenMM, np.random.choice(db.TAG_LIST), 3, 9)[1]

    if line_one == False:
        return False

    line_two = generateLine(givenMM, np.random.choice(db.TAG_LIST), 3, 9, line_one.split()[-1])[1]

    if line_two == False:
        return False

    line_three = generateLine(givenMM, np.random.choice(db.TAG_LIST), 2, 6)[1]

    if line_three == False:
        return False

    line_four = generateLine(givenMM, np.random.choice(db.TAG_LIST), 2, 6, line_three.split()[-1])[1]

    if line_four == False:
        return False

    line_five = generateLine(givenMM, np.random.choice(db.TAG_LIST), 3, 9, line_one.split()[-1])[1]

    if line_five == False:
        return False

    return line_one + '\n' + line_two + '\n' + line_three + '\n' + line_four + '\n' + line_five

def bard_demo():

    """ bard demo function

    Parameters
    --------
    None

    Returns
    --------
    None

    Simply generates a limerick with top survivor, reads the limerick out loud,
    and saves it to a file.
    """

    #choose top survivor
    with open(" Optimization and Model Data/survivors.json", 'r') as f:
        survivors = json.load(f)
    top = max(list(survivors.keys()))
    bestMM = survivors[top]

    with open("demo_lims.json", "r") as f:
        lims = json.load(f)

    #gen a limerick
    new_lim = False
    while new_lim == False:
        new_lim = genLimerick(bestMM)

    #generate audio file of limerick being read, save and read file
    spch = tts.gTTS(text=new_lim, lang='en')
    spch.save("demo.mp3")

    
    print(new_lim)

    #check if any lims have been saved yet, then save lim
    if '0' not in lims:
        lims['0'] = []  
    lims['0'].append(new_lim)

    #save lim to file
    with open("demo_lims.json", "w") as f:
        json.dump(lims, f)


def main():

    db.popTermFromHuman()

    bard_demo()

    return 0


if __name__ == "__main__":
    main()



