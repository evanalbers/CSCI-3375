"""
Learning Objectives
 - let's remember python!
 - What would a Markov Chain look like in code?
"""

import numpy as np

class MarkovMusician:
    def __init__(self, transition_matrix):
        """simulates a musician that relies on a simple Markov Chain.
            Args:
                transition_matric (dict): transition probabilities for the Markov Chain
        """
        self.transition_matrix = transition_matrix
        self.notes = list(transition_matrix.keys())

    def get_next_note(self, current_note):
        """
        Decide the note to play based on the current note.
        Args: 
            current_note (str): the current note being played in our sequence
        """
        return np.random.choice(
            self.notes, 
            p = [self.transition_matrix[current_note][next_note] for next_note in self.notes]
        )
    
    def compose_melody(self, current_note= "A", song_length = 3):
        """
        Generate a sequence of notes.
        Args:
            current_note(str): note of song we're currently looking at
            song_length (int): number of notes per song
        """
        melody = []
        while len(melody) < song_length:
            next_note = self.get_next_note(current_note)
            melody.append(next_note) # remember lists are mutable
            current_note = next_note

        return melody
    """
    For Example:
        np.random.choice(5, p=[0.1, 0, 0.3, 0.6, 0])

        5 => array([0, 1, 2, 3, 4])
        p => probabilities for each of the elements above
    """

def main():
    song_maker = MarkovMusician({
        "A": {"A" : 0.3, "B": 0.4, "C": 0.3},
        "B": {"A" : 0.7, "B": 0.2, "C": 0.1},
        "C": {"A" : 0.1, "B": 0.7, "C": 0.2}
    })

    print(song_maker.transition_matrix)

if __name__ == "__main__":
    main()