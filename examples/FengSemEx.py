import numpy as np
from yamata import *

def FengSemEx():
    code1 = '''
        q :=0;
        H[q];
        if  # M0[q] -> skip
            # M1[q] -> skip end;
        {X[q] || H[q]}
    '''
    vec = np.array([1., 0.])
    vinit = VVec(QVar(['q']), vec)

    fc = compile(code1)
    fc.show("output/flowchart")

    # vec sim
    print(vecsim(fc, vinit, 100, 1000))

    # qts calc
    qts = qtscalc(fc, vinit.outer(), 12)
    qts.show("output/qts")
    qts.reduce().show("output/reduced_qts")

    code2 = '''
        q :=0;
        if  # Mp[q] -> skip
            # Mm[q] -> skip end;
        {X[q] || H[q]}
    '''

    fc = compile(code2)
    fc.show("output/flowchart1")

    # vec sim
    print(vecsim(fc, vinit, 100, 1000))

    # qts calc
    qts = qtscalc(fc, vinit.outer(), 12)
    qts.show("output/qts1")
    qts.reduce().show("output/reduced_qts1")