
from __future__ import annotations
from typing import List

import graphviz

class Vertex:
    def __init__(self, _label):

        # the label for identity of vertices
        self.label = _label 

        # the list of input and output edges
        self.inE : List[Edge] = []
        self.outE : List[Edge] = []
    
    def processed_label(self) -> str:
        txt = str(self.label)

        # if no line breaks
        if txt.find('\n') == -1:
            return txt
        
        txt = txt.replace('\n', '\\l') + "\\l"
        return txt

class Edge:
    def __init__(self, _A : Vertex, _B : Vertex):
        self.A = _A
        self.B = _B


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
    
    def createV(self, label) -> Vertex:
        '''
            Create a new unique vertex in this flowchart, return the vertex.
            (uniqueness check not applied)
        '''
        v = Vertex(label)
        self.vertices.append(v)
        return v
    
    
    def createE(self, e : Edge):
        '''
            Create an edge from A to B.
        '''
        self.edges.append(e)
        e.A.outE.append(e)
        e.B.inE.append(e)

    def show(self, path: str='output'):
        '''
            output the flowchart diagram
        '''
        dot = graphviz.Digraph()
        
        for v in self.vertices:
            print(str(v.label))
            dot.node(str(v.label), v.processed_label(), 
                    shape = "box", style="filled",
                    fontname = "Consolas",
                    labeljust="l")

        for e in self.edges:
            dot.edge(str(e.A.label), str(e.B.label))

        dot.render(path)

    
