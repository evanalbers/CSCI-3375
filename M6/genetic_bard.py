"""
AUTHOR: Evan Albers
DATE: 22 November 2022
PURPOSE: Optimize the Bard Markov weights ST it performs better for bard_trainer

"""
import bard as b
import bard_trainer as bt
import bard_db as db
import numpy as np
from nltk.stem.lancaster import LancasterStemmer
import json
import copy


NUM_EVAL = 10
TOP_X = 25
GEN_DELTAS = []

def mutationTwo(model):

    for entry in list(model.keys()):

        tag = np.random.choice(len(model[entry]))
        multiple = np.random.choice([0.5, 0.6, 0.7, 0.8, 0.9])
        for prob in model[entry]:
            prob *= multiple
        model[entry][tag] = 1 + model[entry][tag] - sum(model[entry])

    return model

def mutationOne(model):

    for entry in list(model.keys()):
        tag_one = np.random.choice(len(model[entry]))
        tag_two = np.random.choice(len(model[entry]))
        add = model[entry][tag_one]
        model[entry][tag_two] += add
        model[entry][tag_one] -= add
    return model

def mutateModel(model):

    mutation = np.random.choice([1, 2])

    if mutation == 1:
        return mutationOne(model)

    elif mutation == 2:
        return mutationTwo(model)



"""use each set of Markov weights to generate n lims, classify them, record proportion """
def evaluateModel(n, model):

    stemmer = LancasterStemmer()
    raw = db.get_raw_training_data("Training Data/lim_data.json")
    words, classes, documents = db.organize_raw_training_data(raw, stemmer)

    lims = []

    b.initializeMarkovMatrices(givenMM=model)

    for num in range(n):

        lim = b.genLimerick()
        if lim != False:
            lims.append(lim)

    num_pass = 0
    delta_avg = 0

    for lim in lims:
        classify_result = bt.classify(words, classes, lim)[0]
        if classify_result[0] == '1':
            num_pass += 1
        else: 
            delta_avg += classify_result[1]
    
    if len(lims) > 0:
        delta_avg = delta_avg / len(lims)
    else: 
        delta_avg = 0
        

    with open("Optimization and Model Data/current_gen.json", "r") as f:
        gen_dict = json.load(f)


    if len(lims) == 0:
        gen_dict[0] = model
    else:
        gen_dict[1-delta_avg] = model

    with open("Optimization and Model Data/current_gen.json", "w") as f:
        json.dump(gen_dict, f)

    return delta_avg

""" function to find Xth percentile markov weights"""
def getTopX(x):

    current_gen = {}

    with open("Optimization and Model Data/current_gen.json", "r") as f:
        current_gen = json.load(f)

    performances = list(current_gen.keys())

    top_x = np.percentile(performances, x, method='closest_observation')

    top_performers = {}

    for iteration in current_gen:
        if iteration >= top_x:
            top_performers[iteration] = current_gen[iteration]

    with open("Optimization and Model Data/survivors.json", "w") as f:
        json.dump(top_performers, f)

def avgModels(m_one, m_two):

    offspring = {}

    for entry in list(m_one.keys()):
        offspring[entry] = [] 
        for num in range(len(m_one[entry])): 
            offspring[entry].append(((m_one[entry][num] + m_two[entry][num]) / 2))
    
    #normalizing
    for entry in list(offspring.keys()):
        offspring[entry][np.random.choice(len(offspring[entry]))] += (1 - sum(offspring[entry]))

    return offspring

""" def cross pollinate, survivors is set of surviving models, n is size of gen """
def crossPollModels(survivors, n):

    offspring = []

    for num in range(n - len(survivors)):

        parent_one = survivors[np.random.choice(list(survivors.keys()))]
        parent_two = survivors[np.random.choice(list(survivors.keys()))]

        offspring.append(mutateModel(avgModels(parent_one, parent_two)))

    return offspring
        

def genGeneration(first_gen, n):

    markovs = []

    if first_gen == True:

        for num in range(n):
            b.initializeMarkovMatrices()
            model_copy = copy.deepcopy(b.MARKOV_MATRICIES)
            markovs.append(model_copy)
    
    else: 
        #handle survivors
        survivors = {}
        with open("Optimization and Model Data/survivors.json", 'r') as f:
            survivors = json.load(f)
        for model in list(survivors.keys()):
            markovs.append(survivors[model])

        #handle offsrping of survivors
        markovs += crossPollModels(survivors, n)

    return markovs

"""run m generations of size n"""
def runGeneration(first_gen, n):

    gen = genGeneration(first_gen, n)

    with open('Optimization and Model Data/current_gen.json', 'w') as f:
        empty = {}
        json.dump(empty, f)

    for num in range(n):
        delta_avg = evaluateModel(NUM_EVAL, gen[num])

    with open('Optimization and Model Data/survivors.json', "w") as f:
        empty = {}
        json.dump(empty, f)

    getTopX(TOP_X)

    return delta_avg
    
""" m is num generations, n num of markovs per gen"""
def runGA(m, n):

    global GEN_DELTAS

    for num in range(m):

        print("GENERATION " + str(num) + " OF " + str(m))
        delta_avg = runGeneration((num == 0), n)

        top_x = {}
        with open("Optimization and Model Data/survivors.json", "r") as f:
            top_x = json.load(f)
        top = max(list(top_x.keys()))

        print("Top performer in generation " + str(num) + " succeeded with rate of " + str(1-float(top)))
        print("Top performer had average delta of " + str(1-delta_avg))

        GEN_DELTAS.append(1-float(top))

        if float(1-float(top)) < 0.5:
            print('RETRAINING CLASSIFER')
            b.genData(50, top_x[top])
            b.trainModel("Training Data/lim_data.json")

def savePerformanceToJson(deltas):

    with open("Optimization and Model Data/genetic_bard.json", "w") as f:
        perf_dict = {}
        for num in range(len(deltas)):  
            perf_dict[num] = deltas[num]
        json.dump(perf_dict, f)



def main():

    global GEN_DELTAS

    db.popTermFromHuman()

    runGA(100, 10)

    savePerformanceToJson(GEN_DELTAS)

    return 0

if __name__ == "__main__":
    main()
    
