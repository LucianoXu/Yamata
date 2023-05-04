
from __future__ import annotations
from typing import List

from graphviz import Digraph

from yamata.backend import OptEnv
from yamata.flowchart.opteval import OptEnv

from .opteval import *

from ..qast import *
from ..backend import *



#################################
# Vertices

class Vertex:
    def __init__(self, _label, _id : int):

        # the label for identity of vertices
        self.label : AstStatement = _label 

        # the unique number assigned to this vertex
        self.id = _id

        # the list of input and output edges
        self.inE : List[Edge] = []
        self.outE : List[Edge] = []

    def semantic_check(self, optlib : OptEnv) -> None:
        '''
            Check whether this vertex is semantically valid with respect to the operator library.
        '''
        raise NotImplementedError()

    def layout(self, dot : Digraph, show_prog = True) -> None:
        '''
        add this vertex to the flowchart
        '''

        raise NotImplementedError()
    
    def processed_label(self) -> str:
        txt = str(self.label)

        # if no line breaks
        if txt.find('\n') == -1:
            return txt
        
        txt = txt.replace('\n', '\\l') + "\\l"
        return txt
    
class TVertex(Vertex):
    '''
    terminal vertex
    '''
    def layout(self, dot: Digraph, show_prog = True) -> None:
        if show_prog:
            label_str = self.processed_label()
        else:
            label_str = str(self.id)

        dot.node(str(self.id), label_str, 
            shape = "doublecircle",
            fontname = "Consolas",
            labeljust="l")
        
    def semantic_check(self, optlib: OptEnv) -> None:
        return  # nothing to check


class OVertex(Vertex):
    '''
    ordinary vertex, one outgoing edge
    '''
    def layout(self, dot: Digraph, show_prog = True) -> None:
        if show_prog:
            label_str = self.processed_label()
        else:
            label_str = str(self.id)

        dot.node(str(self.id), label_str, 
            shape = "box", style="filled",
            fontname = "Consolas",
            labeljust="l")
        
    def semantic_check(self, optlib: OptEnv) -> None:
        return  # nothing to check


class PVertex(Vertex):
    '''
    parallel composition vertex
    '''
    def layout(self, dot: Digraph, show_prog = True) -> None:
        if show_prog:
            label_str = self.processed_label()
        else:
            label_str = str(self.id)

        dot.node(str(self.id), label_str, 
            shape = "box", style="filled", fillcolor = "lightyellow",
            fontname = "Consolas",
            labeljust="l")
        
    def semantic_check(self, optlib: OptEnv) -> None:
        return  # nothing to check

class MVertex(Vertex):
    '''
    measurement vertex
    '''
    def layout(self, dot: Digraph, show_prog = True) -> None:
        if show_prog:
            label_str = self.processed_label()
        else:
            label_str = str(self.id)

        dot.node(str(self.id), label_str, 
            shape = "box", style="filled", fillcolor = "lightblue",
            fontname = "Consolas",
            labeljust="l")
        
    def semantic_check(self, optlib: OptEnv) -> None:
        optsum = VMat.zeroMat()
        for oute in self.outE:
            if isinstance(oute, MEdge):
                opt = mopt_eval(oute.vopt, optlib)
                optsum = optsum + (opt.dagger().mul(opt))
        
        # check the sum
        if not (optsum <= VMat.idMat()):
            raise ValueError("Invalid measurement operator set.")



##################################
# Edges

class Edge:
    def __init__(self, _A : Vertex, _B : Vertex):
        self.A = _A
        self.B = _B

    def semantic_check(self, optlib : OptEnv) -> None:
        '''
            Check whether this vertex is semantically valid with respect to the operator library.
        '''
        raise NotImplementedError()

    def layout(self, dot : Digraph) -> None:
        '''
        add this edge to the flowchart
        '''
        raise NotImplementedError()
        

class IdEdge(Edge):
    '''
    identity edge, going out from parallel composition vertices
    '''
    def layout(self, dot : Digraph) -> None:
        dot.edge(str(self.A.id), str(self.B.id), style = "dotted", arrowhead = "empty")

    def semantic_check(self, optlib: OptEnv) -> None:
        return  # nothing to check


class UEdge(Edge):
    '''
    unitary operation edge
    '''
    def __init__(self, _A: Vertex, _B: Vertex, _vopt: AstVOpt):
        super().__init__(_A, _B)
        self.vopt = _vopt

    def layout(self, dot : Digraph) -> None:
        dot.edge(str(self.A.id), str(self.B.id), 
                label = str(self.vopt), fontname = "Consolas bold")
        
    def semantic_check(self, optlib: OptEnv) -> None:
        try:
            test = uopt_eval(self.vopt, optlib)
        except:
            raise ValueError("Invalid unitary: " + str(self.vopt))


class AEdge(Edge):
    '''
    abort edge
    '''
    def layout(self, dot : Digraph) -> None:
        dot.edge(str(self.A.id), str(self.B.id), color = 'lightgray')
    
    def semantic_check(self, optlib: OptEnv) -> None:
        return  # nothing to check
    

class InitEdge(Edge):
    '''
    initializatoin edge
    '''
    def __init__(self, _A: Vertex, _B: Vertex, _qvar : AstQVar):
        super().__init__(_A, _B)
        self.qvar = _qvar
    
    def layout(self, dot : Digraph) -> None:
        dot.edge(str(self.A.id), str(self.B.id),
                 label = str(self.qvar)+":=0", fontname = "Consolas bold")
        
    def semantic_check(self, optlib: OptEnv) -> None:
        return  # nothing to check



class MEdge(Edge):
    '''
    measurement edge
    '''
    def __init__(self, _A: Vertex, _B: Vertex, _vopt: AstVOpt):
        super().__init__(_A, _B)
        self.vopt = _vopt

    def layout(self, dot: Digraph) -> None:
        dot.edge(str(self.A.id), str(self.B.id), style = "dashed",
                 label = str(self.vopt), fontname = "Consolas bold")
        
    def semantic_check(self, optlib: OptEnv) -> None:
        try:
            test = mopt_eval(self.vopt, optlib)
        except:
            raise ValueError("Invalid measurement branch: " + str(self.vopt))


