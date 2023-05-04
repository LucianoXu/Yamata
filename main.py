
from yamata.qparsing.vparser import parser


if __name__ == "__main__":


    code2 = '''
        while # Mp[x] ->         
            x *= H;
            [ skip || abort; [skip || abort ] || skip ]
        end

        /*
        x *= X;
        [x] *= I;
        if # Mp[x] -> skip;
           # Mm[x] -> skip; end;
        */
    '''

    ast = parser.parse(code2)

    print(ast)

