
from yamata.qparsing.vparser import parser
from yamata.compile.compile import *

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
        [ while # M0[c] ->     
            CX[c t]
        # M1[c] -> end 
        || H[c] ]

    '''

    code2 = '''
        while # M0[c] ->     
            [ CX[c t] || t :=0 ]
        # M1[c] -> end
    '''

    ast = parser.parse(code2)

    print(ast)
    fc = compile_fc(ast)
    fc.show()

