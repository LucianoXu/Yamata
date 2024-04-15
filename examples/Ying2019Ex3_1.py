import numpy as np
from yamata import *

def Ying2019Ex3_1():
    code = '''
        { X[p]; Z[q] || 
            if  # M0[r] -> skip
                # M1[r] -> H[r] end }
    '''
    vec = np.array([1., 0., 0., 0., 0., 0., 0., 1.])/np.sqrt(2)
    vGHZ = VVec(QVar(['p','q','r']), vec)

    fc = compile(code)
    fc.show("output/flowchart")

    # vec sim
    print(vecsim(fc, vGHZ, 100, 1000))

    # qts calc
    qts = qtscalc(fc, vGHZ.outer(), 12)
    qts.show("output/qts")
    qts.reduce().show("output/reduced_qts")