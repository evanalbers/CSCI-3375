"""
Author: Evan Albers
Due Date: 22 November 2022
Purpose: Driver for bard.py, used to run the program, start training, etc.

"""

import bard_db as db
import bard as b
import genetic_bard as gb
from playsound import playsound



def main():

    db.popTermFromHuman()

    with open("bard_intro.txt", "r") as f:
        print(f.read())

        
    u_input = input("What would you like to run? ")
    while u_input != 'q':
        if u_input == 'g':
            b.bard_demo()

        elif u_input == "p":
            playsound("demo.mp3")

        elif u_input.split()[0] == "tb":
            if len(u_input.split()) != 3:
                print("usage: tb [generations] [models per generation]")
                break
            gb.runGA(u_input.split()[1], u_input.split()[2])
        print("Done!")
        u_input = input("What would you like to run? ")

if __name__ == "__main__":
    main()