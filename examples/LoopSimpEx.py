
import numpy as np
from yamata import *


def LoopSimpEx():
    code = '''
        [q] :=0;
        {
            loop
                H[q]
            end
            ||
            if # M0[q] -> skip
                # M1[q] -> X[q]
            end
        }
    '''
    vec = np.array([1., 0.])
    vinit = VVec(QVar(['q']), vec)

    fc = compile(code)
    fc.show("output/flowchart")

    # vec sim
    print(vecsim(fc, vinit, 100, 1000))

    # qts calc
    qts = qtscalc(fc, vinit.outer(), 12)
    qts.show("output/qts")
    qts.reduce().show("output/reduced_qts")
