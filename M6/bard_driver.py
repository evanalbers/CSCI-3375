"""
Author: Evan Albers
Due Date: 22 November 2022
Purpose: Driver for bard.py, used to run the program, start training, etc.

"""

import bard_db as db
import bard as b
import genetic_bard as gb
from playsound import playsound
import json


def main():

    with open("bard_intro.txt", "r") as f:
        print(f.read())

    input = ""
    while input != 'q':
        if input == 'g':
            b.bard_demo()

        elif input == "p":
            playsound("demo.mp3")

        elif input.split()[0] == "tb":
            if len(input.split()) != 3:
                print("usage: tb [generations] [models per generation]")
                break
            gb.runGA(input.split()[1], input.split()[2])



        

if __name__ == "__main__":
    main()