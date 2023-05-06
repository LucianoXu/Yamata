from __future__ import annotations
from typing import Dict, Any

from .backend import *

# Unitaries

unitary_dict = {
    "I" : np.array([[1., 0.],
                    [0., 1.]]),

    "X" : np.array([[0., 1.],
                    [1., 0.]]),

    "Y" : np.array([[0., -1.j],
                    [1.j, 0.]]),

    "Z" : np.array([[1., 0.],
                    [0., -1.]]),

    "H" : np.array([[1., 1.],
                    [1., -1.]])/np.sqrt(2),
    
    "CX" : np.array([[1., 0., 0., 0.],
                     [0., 1., 0., 0.],
                     [0., 0., 0., 1.],
                     [0., 0., 1., 0.]]),

    "SWAP" : np.array([[1., 0., 0., 0.],
                       [0., 0., 1., 0.],
                       [0., 1., 0., 0.],
                       [0., 0., 0., 1.]]),
}

meaopt_dict = {

    "M0" : np.array([[1., 0.],
                     [0., 0.]]),

    "M1" : np.array([[0., 0.],
                     [0., 1.]]),

    "Mp" : np.array([[1., 1.],
                     [1., 1.]])/2.,

    "Mm" : np.array([[1., -1.],
                     [-1., 1.]])/2.,

    "MI" : np.array([[1.]]),

    "MZero" : np.array([[0.]]),

}

class OptEnv:
    def __init__(self):
        self.unitary_opt = {}
        self.measure_opt = {}

    def add_unitary_opt(self, name : str, opt : np.ndarray):
        # TODO #1
        self.unitary_opt[name] = opt

    def add_measure_opt(self, name : str, opt : np.ndarray):
        self.measure_opt[name] = opt

def get_optlib() -> OptEnv:
    lib = OptEnv()

    for name in unitary_dict:
        lib.add_unitary_opt(name, unitary_dict[name])

    for name in meaopt_dict:
        lib.add_measure_opt(name, meaopt_dict[name])

    return lib