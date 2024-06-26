
from __future__ import annotations
from typing import List, Dict

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

    def layout(self, dot : Digraph, show_prog = True, show_id = False,
               asn_label : Dict[int, str] = {}, highlighted = False) -> None:
        '''
        add this vertex to the flowchart
        show_prog: whether to show the remaining program
        show_id : whether to show the vertex id 
        asn_label : whether to display assertion labels
        '''

        # TODO #4

        label_str = ""

        if show_id:
            label_str += "#" + str(self.id)

        if show_prog:
            if show_id:
                label_str += "\n"
            label_str += self.processed_label()

        if self.id in asn_label:
            if show_id or show_prog:
                label_str += "\n\n" 
            label_str += asn_label[self.id]

        self.draw_node(dot, label_str, highlighted)

        return 
    
        # the following code is for html representation  

        label_str = "<"

        if show_id:
            label_str += '''
                <table border="0" cellborder="0" cellpadding="3" bgcolor="white">
                <tr>
                <td bgcolor="black" align="center" colspan="2"><font color="white">#'''\
                + str(self.id) + '''</font></td></tr>'''

        if show_prog:
            label_str += "<tr><td>" + self.processed_label() + "</td></tr>"
        
        label_str += "</table>>"

        dot.node(str(self.id), label_str, 
            shape = "box, bold",
            fontname = "Consolas",
            labeljust="l")
        

    
    def draw_node(self, dot : Digraph, label : str, highlighted = False) -> None:
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
    def draw_node(self, dot : Digraph, label: str, highlighted = False) -> None:
        if highlighted:
            dot.node(str(self.id), label, color = "red",
                shape = "box", style= "bold",
                fontname = "Consolas",
                labeljust="l")
        else:
            dot.node(str(self.id), label,
                shape = "box", style= "bold",
                fontname = "Consolas",
                labeljust="l")


    def semantic_check(self, optlib: OptEnv) -> None:
        return  # nothing to check


class OVertex(Vertex):
    '''
    ordinary vertex, one outgoing edge
    '''
    def draw_node(self, dot: Digraph, label: str, highlighted = False) -> None:
        if highlighted:
            dot.node(str(self.id), label, color = "red",
                shape = "box", style="filled, bold", fillcolor = "lightgray",
                fontname = "Consolas",
                labeljust="l")
        else:
            dot.node(str(self.id), label,
                shape = "box", style="filled",
                fontname = "Consolas",
                labeljust="l")

        
    def semantic_check(self, optlib: OptEnv) -> None:
        return  # nothing to check


class PVertex(Vertex):
    '''
    parallel composition vertex
    '''
    def draw_node(self, dot: Digraph, label: str, highlighted = False) -> None:
        if highlighted:
            dot.node(str(self.id), label, color = "red",
                shape = "box", style="filled, bold", fillcolor = "lightyellow",
                fontname = "Consolas",
                labeljust="l")
        else:
            dot.node(str(self.id), label,
                shape = "box", style="filled", fillcolor = "lightyellow",
                fontname = "Consolas",
                labeljust="l")

        
        
    def semantic_check(self, optlib: OptEnv) -> None:
        return  # nothing to check

class MVertex(Vertex):
    '''
    measurement vertex
    '''
    def draw_node(self, dot: Digraph, label: str, highlighted = False) -> None:
        if highlighted:
            dot.node(str(self.id), label, color = "red",
                shape = "box", style="filled, bold", fillcolor = "lightblue",
                fontname = "Consolas",
                labeljust="l")
        else:
            dot.node(str(self.id), label,
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


