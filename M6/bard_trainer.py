"""
AUTHOR: Evan Albers
PURPOSE: generate a model that does the following:
    - determines the subject of a limerick
    - trains a model identifying human limericks from ones generated by bard.py 
    - output to be used as a metric to hone Bard.py's model, want to be able to fool this algo

"""

import json

def compile_limerick_list(filename):

    with open(filename) as file:

        entries = json.load(file)

        for entry in entries:
            if entry["is_limerick"] == True:
                print(entry["limerick"])




def main():

    compile_limerick_list("limerick_dataset_oedilf_v3.json")

if __name__ == "__main__":
    main()

