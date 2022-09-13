"""
AUTHOR: Evan Albers
DUE DATE: 15 SEPTEMBER 2022
PROJECT: M3
NOTES: Want to think about having turtles that start out "excited" - fast moving, spazzing out, and they lose energy over time
- maybe more excited if there are more of them?
"""



import numpy as np
import turtle as t


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
        

def main():

    roadLessTurtled()
    t.done()
    t.mainloop()
    
    
    


main()
    


    



