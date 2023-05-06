import numpy as np
from yamata import *

def Ying2019Ex5_2():
    code0 = '''
        { H[p]; H[p] || 
          if # M0[p] -> skip
             # M1[p] -> X[q] end }
    '''
    vec = np.array([1., 0., 0., 1.])/np.sqrt(2)
    vbeta = VVec(QVar(['p','q']), vec)

    fc = compile(code0)
    fc.show("output/flowchart")

    # vec sim
    print(vecsim(fc, vbeta, 100, 1000))

    # qts calc
    qts = qtscalc(fc, vbeta.outer(), 15)
    qts.show("output/qts")
    qts.reduce().show("output/reduced_qts")


    code1 = '''
        [ <H[p]; H[p]> || 
          if # M0[p] -> skip
             # M1[p] -> X[q] end ]
    '''

    fc = compile(code1)
    fc.show("output/flowchart1")

    # vec sim
    print(vecsim(fc, vbeta, 100, 1000))

    # qts calc
    qts = qtscalc(fc, vbeta.outer(), 15)
    qts.show("output/qts1")
    qts.reduce().show("output/reduced_qts1")
