'''
    Simulate the calculation through vector state and sampling.
'''


from __future__ import annotations
from typing import List, Tuple

from .backend import *
from .flowchart.vertex_edge import Vertex
from .flowchart.flowchart import Flowchart

class MachineState:
    def __init__(self, _vstate : VVec, _prog : Vertex, _fc : Flowchart):
        self.vstate = _vstate
        self.prog = _prog
        self.fc = _fc