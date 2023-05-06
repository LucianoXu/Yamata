import numpy as np
from yamata import *

def XuDemoEx():
    code = '''
        { while # M0[c] -> CX[c t]
                # M1[c] -> end
          || H[c] }
    '''
    vec = np.array([1., 0., 0., 0.])
    vinit = VVec(QVar(['c','t']), vec)

    fc = compile(code)
    fc.show("output/flowchart")

    # vec sim
    print(vecsim(fc, vinit, 100, 1000))

    # qts calc
    qts = qtscalc(fc, vinit.outer(), 12)
    qts.show("output/qts")
    qts.reduce().show("output/reduced_qts")