
from __future__ import annotations
from typing import List

class Vertex:
    def __init__(self, _label):

        # the label for identity of vertices
        self.label = _label 

        # the list of input and output edges
        self.inE : List[Vertex] = []
        self.outE : List[Vertex] = []
        

class Flowchart:
    def __init__(self):
        
        # all vertices for this flowchart
        self.vertices : List[Vertex] = []

    def findV(self, label) -> None | Vertex:
        '''
            Find the vertex of the given label in the flowchart.
            If not found, return None.
        '''
        for v in self.vertices:
            if v.label == label:
                return v
        return None
    
    def createV(self, label) -> bool:
        '''
            Create a new unique vertex in this flowchart.
            Return whether this action succeeded.
        '''
        if self.findV(label) is not None:
            return False
        
        self.vertices.append(Vertex(label))
        return True

    
