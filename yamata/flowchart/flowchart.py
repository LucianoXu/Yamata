
from __future__ import annotations
from typing import List

from ..qast import *

from graphviz import Digraph


#################################
# Vertices

class Vertex:
    def __init__(self, _label, _id : int):

        # the label for identity of vertices
        self.label = _label 

        # the unique number assigned to this vertex
        self.id = _id

        # the list of input and output edges
        self.inE : List[Edge] = []
        self.outE : List[Edge] = []

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



##################################
# Edges

class Edge:
    def __init__(self, _A : Vertex, _B : Vertex):
        self.A = _A
        self.B = _B

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

class AEdge(Edge):
    '''
    abort edge
    '''
    def layout(self, dot : Digraph) -> None:
        dot.edge(str(self.A.id), str(self.B.id), color = 'lightgray')

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


class Flowchart:
    def __init__(self):
        
        # all vertices for this flowchart
        self.vertices : List[Vertex] = []
        self.edges : List[Edge] = []

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

    def show(self, path: str='output', show_prog = True):
        '''
            output the flowchart diagram
        '''
        dot = Digraph()

        
        for v in self.vertices:
            v.layout(dot, show_prog)

        for e in self.edges:
            e.layout(dot)

        # the invisible initial node
        dot.node('-0','',shape='none')
        dot.edge('-0', '0')

        dot.render(path)

    
