"""
AUTHOR: Evan Albers
DUE DATE: 15 SEPTEMBER 2022
PROJECT: M3
NOTES: Want to think about having turtles that start out "excited" - fast moving, spazzing out, and they lose energy over time
- maybe more excited if there are more of them?
"""


import tkinter
import numpy as np
import turtle as t
import curses as c

NUM_TURTLE = 0

def chooseState(state):

    transition_matrix = {"A" : {"A" : 0.1, "B" : 0.4, "C" : 0.5 },
                         "B" : {"A" : 0.4, "B" : 0.3, "C" : 0.3 },
                         "C" : {"A" : 0.1, "B" : 0.2, "C" : 0.7 }
                         }

    return np.random.choice(list(transition_matrix[state].keys()), 1, list(transition_matrix[state].values()))[0]


def roadLessTurtled():

    transition_matrix = {   0 : {0 : 0.1, 1 : 0.9, 2 : 0, 3 : 0, 4 : 0, 5 : 0, 6 : 0, 7 : 0, 8 : 0, 9 : 0},
                            1 : {0 : 0.2, 1 : 0, 2 : 0.8, 3 : 0, 4 : 0, 5 : 0, 6 : 0, 7 : 0, 8 : 0, 9 : 0},
                            2 : {0 : 0.3, 1 : 0, 2 : 0, 3 : 0.7, 4 : 0, 5 : 0, 6 : 0, 7 : 0, 8 : 0, 9 : 0},
                            3 : {0 : 0.4, 1 : 0, 2 : 0, 3 : 0, 4 : 0.6, 5 : 0, 6 : 0, 7 : 0, 8 : 0, 9 : 0},
                            4 : {0 : 0.5, 1 : 0, 2 : 0, 3 : 0, 4 : 0, 5 : 0.5, 6 : 0, 7 : 0, 8 : 0, 9 : 0},
                            5 : {0 : 0.6, 1 : 0, 2 : 0, 3 : 0, 4 : 0, 5 : 0, 6 : 0.4, 7 : 0, 8 : 0, 9 : 0},
                            6 : {0 : 0.7, 1 : 0.9, 2 : 0, 3 : 0, 4 : 0, 5 : 0, 6 : 0, 7 : 0.3, 8 : 0, 9 : 0},
                            7 : {0 : 0.8, 1 : 0.9, 2 : 0, 3 : 0, 4 : 0, 5 : 0, 6 : 0, 7 : 0, 8 : 0.2, 9 : 0},
                            8 : {0 : 0.9, 1 : 0.9, 2 : 0, 3 : 0, 4 : 0, 5 : 0, 6 : 0, 7 : 0, 8 : 0, 9 : 0.1},
                            9 : {0 : 0.1, 1 : 0.9, 2 : 0, 3 : 0, 4 : 0, 5 : 0, 6 : 0, 7 : 0, 8 : 0, 9 : 0.9},
    }

    for m in range(100):
        turt = t.Turtle()
        turt.penup()
        turt.goto(0, -50)
        turt.pendown()
        state = 0
        turt.speed(0)
        for n in range(m):
            new_state = np.random.choice(list(transition_matrix[state].keys()), 1, list(transition_matrix[state].values()))[0]
            print(new_state)
            if new_state > 0:
                turt.color("black")
                turt.right(30)
                turt.forward(25)
            else:
                turt.color("red")
                turt.left(30)
                turt.forward(25)
            state = new_state
        turt.hideturtle()
        



class HyperTurtle:

    state = "A"

    def __init__(self, x, y):

        global NUM_TURTLE

        NUM_TURTLE += 1

        print("Running init..")

        turt = t.Turtle()
        turt.penup()

        print("Made new turtle...")

        turt.goto(x + NUM_TURTLE, y - NUM_TURTLE)
        turt.pendown()

        for num in range(100 - NUM_TURTLE):

            turt.speed(100 - num + 5 * NUM_TURTLE)
            turt.forward(100 - NUM_TURTLE)

            new_state = chooseState(self.state)

            if new_state == "A":
                turt.color("red")
                turt.right(NUM_TURTLE * 15)
            elif new_state == "B":
                turt.color("blue")
                turt.left(NUM_TURTLE * 15)
            else:
                turt.color("green")
                turt.left(NUM_TURTLE * 180)
            
            self.state = new_state
        
        NUM_TURTLE -= 1
        turt.hideturtle()

def newTurt(x, y):
    
    newguy = t.Turtle()

    newguy.goto(x, y)

def main():

    #print(chooseState("A"))


    #turtle = t.Turtle()
    #t.onscreenclick(HyperTurtle)
    #turtle.forward(100)
    roadLessTurtled()
    t.done()
    t.mainloop()
    
    
    


main()
    


    



