import numpy as np
from yamata import *

def Ying2019Ex3_2():
    code = '''
        { if # M0[q1] -> skip
             # M1[q1] -> skip end;
          while # M0[q1] -> skip
                # M1[q1] -> end || 
          if # M0[q2] -> skip
             # M1[q2] -> skip end;
          while # M0[q2] -> skip
                # M1[q2] -> end }
    '''
    vec = np.array([1., 1., 1., 1.])/2
    vpp = VVec(QVar(['q1','q2']), vec)

    fc = compile(code)
    fc.show("output/flowchart")

    # vec sim
    print(vecsim(fc, vpp, 100, 1000))

    # qts calc
    qts = qtscalc(fc, vpp.outer(), 12)
    qts.show("output/qts")
    qts.reduce().show("output/reduced_qts")