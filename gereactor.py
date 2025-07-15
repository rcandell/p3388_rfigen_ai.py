import numpy as np

class GEReactor:
    """
    A two-state Markov chain reactor.

    This class implements a two-state Markov chain, often used in models like
    the Gilbert-Elliott model for simulating bursty behavior (e.g., ON/OFF states
    in RFI systems). The state transitions are determined by a 2x2 probability
    matrix, where only the diagonal elements are used: probs[0,0] is the
    probability of staying in state 0, and probs[1,1] is the probability of
    staying in state 1. The object starts in state 0.

    Attributes:
        state (int): Current state (0 or 1).
        probs (numpy.ndarray): 2x2 transition probability matrix (only diagonal elements used).

    Methods:
        __init__(probs): Initialize with probability matrix.
        step(): Update the state based on transition probabilities.

    Author: Rick Candell
    (c) Copyright Rick Candell All Rights Reserved
    """
    
    def __init__(self, probs):
        """
        Initialize the GEReactor with a transition probability matrix.

        Args:
            probs (numpy.ndarray): 2x2 matrix where probs[0,0] is P(0->0) and probs[1,1] is P(1->1).
        """
        self.state = 0  # Current state of the reactor (0 or 1)
        self.probs = np.array(probs)  # 2x2 transition probability matrix
    
    def step(self):
        """
        Update the state of the reactor based on transition probabilities.

        Generates a random number and decides whether to transition to the other state
        or stay in the current state based on the probabilities stored in self.probs.

        Transition logic:
            - In state 0: if rand() > self.probs[0,0], transition to state 1
            - In state 1: if rand() > self.probs[1,1], transition to state 0
        Thus, P(0->0) = probs[0,0], P(0->1) = 1 - probs[0,0],
             P(1->1) = probs[1,1], P(1->0) = 1 - probs[1,1].
        """
        r = np.random.rand()
        if self.state == 0:  # in state 0
            if r > self.probs[0, 0]:
                self.state = 1
        else:  # in state 1
            if r > self.probs[1, 1]:
                self.state = 0
        return self