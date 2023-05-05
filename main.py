
from yamata.compile import compile
from yamata.vecSim import *
from yamata.backend import *
from yamata.qtscalc import *

if __name__ == "__main__":


    code2 = '''
        while # Mp[x] ->         
            x *= H;
            [ skip || abort ]
        end;
        x *= X

        /*
        [x] *= I;
        if # Mp[x] -> skip
           # Mm[x] -> skip
        else
            abort
        end
        */
    '''
    code2 = '''
        while # M0[c] ->     
            [ H[c] || skip ]
        # M1[c] -> end
    '''

    code_example = '''
        [ while # M0[c] ->     
            CX[c t]
        # M1[c] -> end 
        || H[c]]

    '''

    code2 = '''
        c :=0
    '''

    vinit = VVec(QVar(['c', 't']), np.array([1., 0., 0., 0.]))
    vbeta = VVec(QVar(['c', 't']), np.array([1., 0., 0., 1.])/np.sqrt(2))
    v0 = VVec(QVar(['c', 't']), np.array([0., 0., 1., 1.])/np.sqrt(2))

    rhoinit = VMat(QVar(['c', 't']), 
                   np.array([[1., 0., 0., 0.],
                             [0., 0., 0., 0.],
                             [0., 0., 0., 0.],
                             [0., 0., 0., 0.]]))

    optlib = get_optlib()
    fc = compile(code_example, optlib, "output")


    # qtscalc
    qts = qtscalc(fc, rhoinit, 10)

    qts.show()

    qts.reduce().show("reduced")

    exit()


    # vecsim
    res = vecsim(fc, v0, 100, 1000)
    print(res)



