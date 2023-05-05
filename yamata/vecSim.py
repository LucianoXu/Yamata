'''
    Simulate the calculation through vector state and sampling.
'''


from __future__ import annotations
from typing import List, Tuple, Dict

from .backend import *
from .flowchart.vertex_edge import *
from .flowchart.flowchart import Flowchart

import random
from tqdm import tqdm

class MachineState:
    def __init__(self, _vstate : VVec, _vertex : Vertex):
        self.vstate = _vstate
        self.vertex = _vertex

    def next(self, fc : Flowchart) -> MachineState | None:
        '''
            Conduct one step of calculation and return the next machine state.
            Return [None] if the machine already terminates.
        '''

        # stop 
        if isinstance(self.vertex, TVertex):
            return None
        
        if len(self.vertex.outE) == 1:
            e = self.vertex.outE[0]
            if isinstance(e, IdEdge):
                return MachineState(self.vstate, e.B)
            
            if isinstance(e, UEdge):
                uopt = uopt_eval(e.vopt, fc.optlib)
                return MachineState(self.vstate.Mapply(uopt), e.B)
            
            if isinstance(e, AEdge):
                # directly shutdown
                return None
            
            if isinstance(e, InitEdge):
                # Note: initialization is interpreted as multiple [if - skip - X gate] statements
                raise NotImplementedError()

        if isinstance(self.vertex, PVertex):
            # make an arbitrary choice
            e = random.choice(self.vertex.outE)
            return MachineState(self.vstate, e.B)
        
        if isinstance(self.vertex, MVertex):
            # calculate probabilities
            prob : List[float] = []
            mea_stt : List[VVec] = []

            for i in range(len(self.vertex.outE)):
                e = self.vertex.outE[i]
                if not isinstance(e, MEdge):
                    raise Exception()
                mopt = mopt_eval(e.vopt, fc.optlib)
                # calculate the state vectors after measurements
                v = self.vstate.Mapply(mopt)
                mea_stt.append(v)
                prob.append(v.norm2())

            # make a sampling
            res = sampling(prob)

            # unterminated state
            if res == -1:
                return None
            
            return MachineState(mea_stt[res].normalized(), self.vertex.outE[res].B)

        raise Exception()
                

class VecRecord:
    '''
    One VecRecord contains all information about one vector result in a simulation experiment.
    '''
    def __init__(self, _stt : VVec | None):
        self.stt = _stt

        # the count of running step of all cases
        self.step_count : List[int] = []

    def __len__(self) -> int:
        return len(self.step_count)
    
    def append(self, count : int) -> None:
        return self.step_count.append(count)
    
    def __str__(self) -> str:
        if self.stt is None:
            label = "Unterminated"
        else:
            label = str(self.stt)
        return label + " - " + str (len(self.step_count)) + "\n"

class VecSimRes:
    '''
    The result for a vector simulation.
    '''
    def __init__(self, _fc : Flowchart, _vinit : VVec, _step_bound : int):
        self.fc = _fc
        self.vinit = _vinit
        self.step_bound = _step_bound

        # Here [None] represents unterminated states
        self.records : List[VecRecord] = [VecRecord(None)]

    def record(self, stt : VVec|None, count : int) -> None:
        # if this state already exists
        for rec in self.records:
            if rec.stt == stt:
                rec.append(count)
                return

        # if it is a new state
        new_rec = VecRecord(stt)
        self.records.append(new_rec)
        new_rec.append(count)

    def __str__(self) -> str:
        r = ""
        for rec in self.records:
            r += str(rec)
        return r





def vecsim(fc : Flowchart, vinit : VVec, step_bound = 500, sampling_count = 1) -> VecSimRes:
    '''
    conduct the vector simulation on flowchart [fc]
    fc : compiled flowchart
    vinit : initial quantum state vector (normalized)
    step_bound : maximum count of executed steps. The machine will stop in the unterminated state afterwards.
    sampling_count : number of sampling
    '''

    random.seed()

    # check the initial state vector
    vnorm2 = vinit.norm2()
    if  vnorm2 > 1. + vinit.eps or vnorm2 < 1. - vinit.eps:
        raise ValueError("Invalid initial state vector")
    
    res = VecSimRes(fc, vinit, step_bound)
    ms = MachineState(vinit, fc.vertices[0])

    for count in tqdm(range(sampling_count), desc = "Sampling"):
        cur_ms : MachineState = ms

        next_ms = None
        for step in range(step_bound):
            next_ms = cur_ms.next(fc) 
            if next_ms is None:
                # record the state
                res.record(cur_ms.vstate, step)
                break
            cur_ms = next_ms

        # record the state
        if next_ms is not None:
            res.record(None, step_bound)

    return res


