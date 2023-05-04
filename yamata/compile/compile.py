from __future__ import annotations
from typing import List

from ..flowchart.flowchart import *
from ..qparsing.qast import *


def next(ast : AstStatement) -> List[AstStatement]:
    '''
        return the abstract syntax tree for the next step.
        The None means the terminal vertex.
    '''
    if isinstance(ast, AstTerminal):
        return []
    elif isinstance(ast, AstSkip):
        return [AstTerminal()]
    elif isinstance(ast, AstAbort):
        return [AstTerminal()]
    elif isinstance(ast, AstInit):
        return [AstTerminal()]
    elif isinstance(ast, AstUnitary):
        return [AstTerminal()]
    elif isinstance(ast, AstIf):
        return [guard.prog for guard in ast.ls] + [ast.default_prog]
    elif isinstance(ast, AstWhile):
        return [AstSeq(ast.body.prog, ast), AstTerminal()]
    elif isinstance(ast, AstSeq):
        # case on S0
        next_S0_ls = next(ast.S0)
        next_seq = []
        for next_S0 in next_S0_ls:
            if isinstance(next_S0, AstTerminal):
                next_seq.append(ast.S1)
            else:
                next_seq.append(AstSeq(next_S0, ast.S1))
        return next_seq
    
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
                
                # else branch
                new_para = ast.ls.copy()
                new_para[i] = ast_i.default_prog
                next_para.append(AstIf(new_guarded, AstParallel(new_para)))

            elif isinstance(ast_i, AstWhile):
                # expand while to a if statement
                new_para = ast.ls.copy()
                new_para[i] = AstSeq(ast_i.body.prog, ast_i)
                new_guarded = [AstGuardedProg(ast_i.body.vopt, AstParallel(new_para))]

                # else branch
                new_para = ast.remove(i)
                next_para.append(AstIf(new_guarded, new_para))

            elif isinstance(ast_i, AstSeq):
                # match S0
                if isinstance(ast_i.S0, AstIf):
                    # process every guarded command
                    new_guarded = ast_i.S0.ls.copy()
                    for j in range(len(ast_i.S0.ls)):
                        new_para = ast.ls.copy()
                        # sequential composition here
                        new_para[i] = AstSeq(ast_i.S0.ls[j].prog, ast_i.S1)
                        new_guarded[j].prog = AstParallel(new_para)
                    
                    # else branch
                    new_para = ast.ls.copy()
                    # sequential composition here
                    new_para[i] = AstSeq(ast_i.S0.default_prog, ast_i.S1)
                    next_para.append(AstIf(new_guarded, AstParallel(new_para)))
                
                if isinstance(ast_i.S0, AstWhile):
                    # expand while to a if statement
                    new_para = ast.ls.copy()
                    # sequential composition here
                    new_para[i] = AstSeq(ast_i.S0.body.prog, ast_i)
                    new_guarded = [AstGuardedProg(ast_i.S0.body.vopt, AstParallel(new_para))]

                    # else branch
                    new_para = ast.ls.copy()
                    new_para[i] = ast_i.S1
                    next_para.append(AstIf(new_guarded, AstParallel(new_para)))

                if isinstance(ast_i.S0, AstSkip) or isinstance(ast_i.S0, AstAbort)\
                    or isinstance(ast_i.S0, AstInit) or isinstance(ast_i.S0, AstUnitary):
                    new_para = ast.ls.copy()
                    new_para[i] = ast_i.S1
                    next_para.append(AstSeq(ast_i.S0, AstParallel(new_para)))

                else:
                    raise Exception()
            
            elif isinstance(ast_i, AstSkip) or isinstance(ast_i, AstAbort)\
                or isinstance(ast_i, AstInit) or isinstance(ast_i, AstUnitary):
                
                next_para.append(AstSeq(ast_i, ast.remove(i)))
            
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
    next_label = next(v.label)
    for lb in next_label:
        # if [fc] does not contain the next vertex [u] yet
        u = fc.findV(lb)
        if u is None:
            u = fc.createV(lb)
            extend_fc(fc, u)
        new_e = Edge(v, u)
        fc.createE(new_e)
                

    