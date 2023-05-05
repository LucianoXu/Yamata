'''

    The compiler for transforming program syntacies to flowcharts.


'''



from __future__ import annotations
from typing import List, Tuple

from .qparsing.vparser import parser
from .flowchart.flowchart import Flowchart, Vertex

from .backend import OptEnv

from .qast import *
from copy import deepcopy


def next(ast : AstStatement) -> List[Tuple[AstStatement|AstVOpt|None, AstStatement]]:
    '''
        return the abstract syntax tree for the next step.
        result: a tuple, first element is the transformation, 
            and the second element is the next program syntax
    '''
    if isinstance(ast, AstTerminal):
        return []
    elif isinstance(ast, AstSkip):
        return [(ast, AstTerminal())]
    elif isinstance(ast, AstAbort):
        return [(ast, AstTerminal())]
    elif isinstance(ast, AstInit):
        return [(ast, AstTerminal())]
    elif isinstance(ast, AstUnitary):
        return [(ast, AstTerminal())]
    elif isinstance(ast, AstIf):
        return [(guard.vopt, guard.prog) for guard in ast.ls]
    elif isinstance(ast, AstWhile):
        return [(ast.body.vopt, AstSeq(ast.body.prog, ast)), 
                (ast.term_vopt, AstTerminal())]
    elif isinstance(ast, AstSeq):
        # case on S0
        next_S0_ls = next(ast.S0)
        next_seq : List[Tuple[AstStatement|AstVOpt|None, AstStatement]] = []
        for next_pair in next_S0_ls:
            if isinstance(next_pair[1], AstTerminal):
                next_seq.append((next_pair[0], ast.S1))
            else:
                next_seq.append((next_pair[0], AstSeq(next_pair[1], ast.S1)))
        return next_seq
    
    elif isinstance(ast, AstParallel):
        next_para : List[Tuple[AstStatement|AstVOpt|None, AstStatement]] = []
        for i in range(len(ast.ls)):
            ast_i = ast.ls[i]
            if isinstance(ast_i, AstIf):
                # process every guarded command
                new_guarded = deepcopy(ast_i.ls)
                for j in range(len(ast_i.ls)):
                    new_para = ast.ls.copy()
                    new_para[i] = ast_i.ls[j].prog
                    new_guarded[j].prog = AstParallel(new_para)
                
                next_para.append((None, AstIf(new_guarded)))

            elif isinstance(ast_i, AstWhile):
                # expand while to a if statement
                new_para = ast.ls.copy()
                new_para[i] = AstSeq(ast_i.body.prog, ast_i)
                new_guarded = [AstGuardedProg(ast_i.body.vopt, AstParallel(new_para))]

                # else branch
                new_guarded.append(AstGuardedProg(ast_i.term_vopt, ast.remove(i)))
                next_para.append((None, AstIf(new_guarded)))

            elif isinstance(ast_i, AstSeq):
                # match S0
                if isinstance(ast_i.S0, AstIf):
                    # process every guarded command
                    new_guarded = deepcopy(ast_i.S0.ls)
                    for j in range(len(ast_i.S0.ls)):
                        new_para = ast.ls.copy()
                        # sequential composition here
                        new_para[i] = AstSeq(ast_i.S0.ls[j].prog, ast_i.S1)
                        new_guarded[j].prog = AstParallel(new_para)
                    
                    next_para.append((None, AstIf(new_guarded)))
                
                elif isinstance(ast_i.S0, AstWhile):
                    # expand while to a if statement
                    new_para = ast.ls.copy()
                    # sequential composition here
                    new_para[i] = AstSeq(ast_i.S0.body.prog, ast_i)
                    new_guarded = [AstGuardedProg(ast_i.S0.body.vopt, AstParallel(new_para))]

                    # else branch
                    new_para = ast.ls.copy()
                    new_para[i] = ast_i.S1
                    new_guarded.append(AstGuardedProg(ast_i.S0.term_vopt, AstParallel(new_para)))
                    next_para.append((None, AstIf(new_guarded)))

                elif isinstance(ast_i.S0, AstSkip) or isinstance(ast_i.S0, AstAbort)\
                    or isinstance(ast_i.S0, AstInit) or isinstance(ast_i.S0, AstUnitary):
                    new_para = ast.ls.copy()
                    new_para[i] = ast_i.S1
                    next_para.append((None, AstSeq(ast_i.S0, AstParallel(new_para))))

                else:
                    raise Exception()
                

            elif isinstance(ast_i, AstSkip) or isinstance(ast_i, AstAbort)\
                or isinstance(ast_i, AstInit) or isinstance(ast_i, AstUnitary):
                
                next_para.append((None, AstSeq(ast_i, ast.remove(i))))
            
            else:
                raise Exception()
            
        return next_para

    else:
        raise Exception()


def compile_fc(ast : AstStatement) -> Flowchart:
    fc = Flowchart()
    v = fc.createV(ast)
    extend_fc(fc, v)
    return fc

def extend_fc(fc : Flowchart, v : Vertex):
    '''
       This method is invocated only when [fc] contains [ast].
    '''
    next_pairs = next(v.label)
    for pair in next_pairs:
        # if [fc] does not contain the next vertex [u] yet
        u = fc.findV(pair[1])
        if u is None:
            u = fc.createV(pair[1])
            extend_fc(fc, u)

        fc.createE(pair[0], v, u)
                



######################################################
# interface

def compile(code : str, optlib : OptEnv, 
            output_path : str | None = None, show_prog = True) -> Flowchart:
    '''
        compile the code string to a flowchart.
        output_path : whether to output the diagram
        show_prog : will replace program codes with vertex numbers if set to False
    '''

    ast = parser.parse(code)

    # compile abstract syntax tree to flowchart
    fc = compile_fc(ast)

    # flowchart: semantic check with operator library
    fc.semantic_check(optlib)

    if output_path is not None:
        fc.show(path = output_path, show_prog = show_prog)

    return fc
    