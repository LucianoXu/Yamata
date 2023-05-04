
from yamata.compile import compile
from yamata.backend import *

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
            [ CX[c t] || t :=0 ]
        # M1[c] -> end
    '''

    code2 = '''
        [ while # M0[c] ->     
            CX[c t]
        # M1[c] -> end 
        || H[c] || skip ]

    '''


    optlib = get_optlib()

    compile(code2, optlib, "output")
