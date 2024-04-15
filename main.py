
import numpy as np
from yamata import *
from examples import *
from yamata.qtscalc import *

from yamata.qparsing.vparser import parser
from yamata.compile import compile_fc

if __name__ == "__main__":

    
    # XuDemoEx()

    # exit()
    

    code = '''
        { A1[q]; A2[q] || A1[q]; A2[q] || A1[q]; A2[q] }
    '''

    
    ast = parser.parse(code)

    # compile abstract syntax tree to flowchart
    fc = compile_fc(ast)
    print(len(fc.vertices))
    # fc.show("output/flowchart", False, True)
    fc.show("output/flowchart")
    exit()
    

    vec = np.array([1., 0.])
    vinit = VVec(QVar(['q']), vec)

    fc = compile(code)
    fc.show("output/flowchart", False, True)
    # fc.show_neighbour(5, "output/neighbour")

    # vec sim
    print(vecsim(fc, vinit, 100, 200))

    # qts calc
    qts = qtscalc(fc, vinit.outer(), 12)
    qts.show("output/qts")
    qts.reduce().show("output/reduced")

