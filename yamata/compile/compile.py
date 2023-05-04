from __future__ import annotations
from typing import List

from ..flowchart.flowchart import *
from ..qparsing.qast import *

def parallel_simplify(ast: AstParallel) -> AstStatement:
    '''
    here we require that at least one component is not None
    '''
    pass

def next(ast : AstStatement) -> List[AstStatement|None]:
    '''
        return the abstract syntax tree for the next step.
        The None means the terminal vertex.
    '''
    if isinstance(ast, AstSkip):
        return [None]
    elif isinstance(ast, AstAbort):
        return [None]
    elif isinstance(ast, AstInit):
        return [None]
    elif isinstance(ast, AstUnitary):
        return [None]
    elif isinstance(ast, AstIf):
        return [guard.prog for guard in ast.ls]
    elif isinstance(ast, AstWhile):
        return [ast.body.prog, None]
    elif isinstance(ast, AstSeq):
        # case on S0
        next_S0_ls = next(ast.S0)
        next_seq = []
        for next_S0 in next_S0_ls:
            if next_S0 is None:
                next_seq.append(ast.S1)
            else:
                next_seq.append(AstSeq(next_S0, ast.S1))
    elif isinstance(ast, AstParallel):
        next_para = []
        for i in range(len(ast.ls)):
            ast_i = ast.ls[i]
            if isinstance(ast_i, AstIf):
                # process every guarded command
                new_guarded = ast_i.ls.copy()
                for j in range(len(ast_i.ls)):
                    new_para = ast.ls.copy()
                    new_para[i] = ast_i.ls[j].prog
                    new_guarded[j].prog = AstParallel(new_para)
                next_para.append(AstIf(new_guarded))

            elif isinstance(ast_i, AstWhile):
                # expand while to a if statement
                new_guarded = []
                



    else:
        raise Exception()
    

