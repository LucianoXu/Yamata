from __future__ import annotations
from typing import List

import numpy as np

def ls_uniqueness_check(ls : List) -> bool:
    '''
    Checks whether all elements in the list are different from each other.
    '''
    for i in range(len(ls)):
        for j in range(i + 1, len(ls)):
            if ls[i] == ls[j]:
                return False
    return True