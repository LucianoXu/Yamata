
from __future__ import annotations
from typing import List

from ..qast import *
from ..backend import *

from .vertex_edge import *

from graphviz import Digraph

class Flowchart:
    def __init__(self):
        
        # all vertices for this flowchart
        self.vertices : List[Vertex] = []
        self.edges : List[Edge] = []
        self._optlib : OptEnv | None = None

    @property
    def optlib(self) -> OptEnv:
        if self._optlib is None:
            raise ValueError("Operator libarary not designated.")
        
        return self._optlib

    def findV(self, label) -> None | Vertex:
        '''
            Find the vertex of the given label in the flowchart.
            If not found, return None.
        '''
        for v in self.vertices:
            if v.label == label:
                return v
        return None
    
    def createV(self, label : AstStatement) -> Vertex:
        '''
            Create a new unique vertex in this flowchart, return the vertex.
            (uniqueness check not applied)
        '''
        if isinstance(label, AstTerminal):
            v = TVertex(label, len(self.vertices))
        elif isinstance(label.first(), AstIf) or isinstance(label.first(), AstWhile):
            v = MVertex(label, len(self.vertices))
        elif isinstance(label.first(), AstParallel):
            v = PVertex(label, len(self.vertices))
        else:
            v = OVertex(label, len(self.vertices))

        self.vertices.append(v)
        return v
    
    
    def createE(self, branch : AstStatement | AstVOpt | None , vA: Vertex, vB: Vertex):
        '''
            Create an edge from vA to vB.
        '''
        if branch is None:
            e = IdEdge(vA, vB)
        elif isinstance(branch, AstVOpt):
            e = MEdge(vA, vB, branch)
        elif isinstance(branch, AstSkip):
            e = IdEdge(vA, vB)
        elif isinstance(branch, AstAbort):
            e = AEdge(vA, vB)
        elif isinstance(branch, AstInit):
            e = InitEdge(vA, vB, branch.qvar)
        elif isinstance(branch, AstUnitary):
            e = UEdge(vA, vB, branch.vopt)
        else:
            raise Exception()

        self.edges.append(e)
        e.A.outE.append(e)
        e.B.inE.append(e)

    def show(self, path: str='flowchart', show_prog = True, show_id = False, 
             asn_label : Dict[int, str] = {}):
        '''
            output the flowchart diagram
        '''
        dot = Digraph()

        
        for v in self.vertices:
            v.layout(dot, show_prog, show_id, asn_label)

        for e in self.edges:
            e.layout(dot)

        # the invisible initial node
        dot.node('-0','',shape='none')
        dot.edge('-0', '0')

        dot.render(path)

    def semantic_check(self, optlib : OptEnv) -> None:
        '''
            Check whether the flowchart is semantically valid with respect to the 
            operator library [optlib].
        '''

        self._optlib = optlib

        for e in self.edges:
            e.semantic_check(optlib)
        
        for v in self.vertices:
            v.semantic_check(optlib)


    
