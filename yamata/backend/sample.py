from __future__ import annotations
from typing import List, Type, Tuple

import random

from .backend import VTerm



def sampling(prob : List[float]) -> int:
    '''
        Do a sampling according to the probability distribution given by prob.
        return the sample result, in number
        if -1 is returned, it means the sample result falls into the ''otherwise'' situation,
            (probability sums to less than 1)
    '''
    # check the distribution
    if sum(prob) > 1. + VTerm.eps_value or min(prob) < - VTerm.eps_value:
        raise ValueError("Invalid probabilistic distribution.")

    # get random number
    r = random.random()

    # compare it with the cumulative distribution sum
    s = 0.
    for i in range(len(prob)):
        s += prob[i]
        if r < s:
            return i
        
    return -1

    




    