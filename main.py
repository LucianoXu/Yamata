
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
            [c t] *= CX
        end 
        || c *= H]

    '''

    ast = parser.parse(code2)

    fc = compile_fc(ast)
    fc.show()

