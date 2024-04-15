import numpy as np
from yamata import *

def Ying2019Ex6_2():
    code = '''
        { 
            q1 :=0; H[q1]; CX[q1 r] ||
            q2 :=0; H[q2]; CX[q2 r]
        }
    '''
    vec = ((np.sqrt(2) + 1)/4) * np.array([1., 1., 0., 0., 0., 0., 0., 0.])\
        + ((np.sqrt(2) - 1)/4) * np.array([0., 0., 0., 0., 0., 0., 1., 1.])\
        + 1./4 * np.array([0., 0., 1., 1., 1., 1., 0., 0.])

    vinit = VVec(QVar(['q1', 'q2', 'r']), vec)

    fc = compile(code)
    fc.show("output/flowchart")

    # vec sim
    print(vecsim(fc, vinit, 100, 1000))

    # qts calc
    qts = qtscalc(fc, vinit.outer(), 12)
    qts.show("output/qts")
    qts.reduce().show("output/reduced_qts")