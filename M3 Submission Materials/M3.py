"""
AUTHOR: Evan Albers
DUE DATE: 15 SEPTEMBER 2022
PROJECT: M3
NOTES: Want to think about having turtles that start out "excited" - fast moving, spazzing out, and they lose energy over time
- maybe more excited if there are more of them?
"""




import numpy as np
import turtle as t
import sys    

def roadLessTurtled(tuning_coeff):

    if type(tuning_coeff) == float and tuning_coeff < 1:
        tuning_coeff = 1
    else: 
        tuning_coeff = int(tuning_coeff)


    prob = 0.1 / int(tuning_coeff)

    transition_matrix = {   0 : {0 : prob, 1 : 1-prob, 2 : 0, 3 : 0, 4 : 0, 5 : 0, 6 : 0, 7 : 0, 8 : 0, 9 : 0},
                            1 : {0 : 2 * prob, 1 : 0, 2 : 1-( 2* prob), 3 : 0, 4 : 0, 5 : 0, 6 : 0, 7 : 0, 8 : 0, 9 : 0},
                            2 : {0 : 3 * prob, 1 : 0, 2 : 0, 3 :  1-(3 * prob), 4 : 0, 5 : 0, 6 : 0, 7 : 0, 8 : 0, 9 : 0},
                            3 : {0 : 4 * prob, 1 : 0, 2 : 0, 3 : 0, 4 : 1-(4 * prob), 5 : 0, 6 : 0, 7 : 0, 8 : 0, 9 : 0},
                            4 : {0 : 5 * prob, 1 : 0, 2 : 0, 3 : 0, 4 : 0, 5 : 1-(5 * prob), 6 : 0, 7 : 0, 8 : 0, 9 : 0},
                            5 : {0 : 6 * prob, 1 : 0, 2 : 0, 3 : 0, 4 : 0, 5 : 0, 6 : 1-(6 * prob), 7 : 0, 8 : 0, 9 : 0},
                            6 : {0 : 7 * prob, 1 : 0, 2 : 0, 3 : 0, 4 : 0, 5 : 0, 6 : 0, 7 : 1-(7 * prob), 8 : 0, 9 : 0},
                            7 : {0 : 8 * prob, 1 : 0, 2 : 0, 3 : 0, 4 : 0, 5 : 0, 6 : 0, 7 : 0, 8 : 1-(8 * prob), 9 : 0},
                            8 : {0 : 9 * prob, 1 : 0, 2 : 0, 3 : 0, 4 : 0, 5 : 0, 6 : 0, 7 : 0, 8 : 0, 9 :1-(9 * prob)},
                            9 : {0 : prob, 1 : 0, 2 : 0, 3 : 0, 4 : 0, 5 : 0, 6 : 0, 7 : 0, 8 : 0, 9 : 1 - prob},
    }

    #printing out the tuning coefficient
    text_turt = t.Turtle()
    text_turt.penup()
    text_turt.goto(-50, 200)
    text_turt.write("Tuning Coefficient: " + str(tuning_coeff), move=False, align="left", font="Verdana")
    text_turt.hideturtle()

    #for each turtle
    for m in range(25):
        turt = t.Turtle()
        turt.penup()
        turt.goto(0, -50)
        turt.pendown()
        state = 0
        turt.speed(0)
        
        #24 total line segments, each time select new state and proceed
        for n in range(24):
            new_state = np.random.choice(list(transition_matrix[state].keys()), 1, True, list(transition_matrix[state].values()))[0]
            
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

    

    roadLessTurtled(sys.argv[1])
    t.done()
    
    
    


main()
    


    



