# ------------------------------------------------------------
# vparser.py
#
# parser
# ------------------------------------------------------------

from __future__ import annotations
from typing import Any, List

import ply.yacc as yacc

from .vlexer import tokens, lexer
from .. import qast


# This is the grammar of a program

def p_prog(p):
    '''
    prog    : statement 
            | seq
    '''
    p[0] = p[1]

    if p[0] is None:
        raise Exception()

# single statements

def p_statement(p):
    '''
    statement   : skip
                | abort
                | init
                | unitary
                | if
                | while
                | parallel
                | atom
                | loop
    '''
    p[0] = p[1]
    
    if p[0] is None:
        raise Exception()
    

def p_skip(p):
    '''
    skip    : SKIP
    '''
    p[0] = qast.AstSkip()

    if p[0] is None:
        raise Exception()

def p_abort(p):
    '''
    abort   : ABORT
    '''
    p[0] = qast.AstAbort()

    if p[0] is None:
        raise Exception()

def p_init(p):
    '''
    init    : ID INIT
            | qvar INIT
    '''
    if isinstance(p[1], qast.AstQVar):
        p[0] = qast.AstInit(p[1])
    else:
        qvar = qast.AstQVar([p[1]])
        p[0] = qast.AstInit(qvar)

    if p[0] is None:
        raise Exception()


def p_unitary(p):
    '''
    unitary : vopt
    '''
    p[0] = qast.AstUnitary(p[1])

    if p[0] is None:
        raise Exception()
    

def p_if(p):
    '''
    if      : IF guarded_prog_ls END
    '''
    p[0] = qast.AstIf(p[2])

    if p[0] is None:
        raise Exception()
    
def p_guarded_prog_ls(p):
    '''
    guarded_prog_ls : guarded_prog
                    | guarded_prog_ls guarded_prog
    '''

    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

    if p[0] is None:
        raise Exception()
    

def p_while(p):
    '''
    while   : WHILE guarded_prog '#' vopt GUARD END
    '''

    p[0] = qast.AstWhile(p[2], p[4])

    if p[0] is None:
        raise Exception()

def p_parallel(p):
    '''
    parallel    : parallel_head '}'
    '''

    p[0] = p[1]

    if p[0] is None:
        raise Exception()
    
def p_parallel_head(p):
    '''
    parallel_head   : '{' prog PARALLEL prog
                    | parallel_head PARALLEL prog
    '''

    if len(p) == 5:
        p[0] = qast.AstParallel([p[2], p[4]])
    elif len(p) == 4:
        p[0] = p[1].appended(p[3])
    else:
        raise Exception()

    if p[0] is None:
        raise Exception()
    
def p_atom(p):
    '''
    atom    : '<' prog '>'
    '''

    p[0] = qast.AstAtom(p[2])

    if p[0] is None:
        raise Exception()
    
def p_loop(p):
    '''
    loop    : LOOP prog END
    '''
    
    p[0] = qast.AstLoop(p[2])

    if p[0] is None:
        raise Exception()
    
def p_seq(p):
    '''
    seq     : statement ';' prog
    '''
    p[0] = qast.AstSeq(p[1], p[3])

    if p[0] is None:
        raise Exception()


def p_guarded_prog(p):
    '''
    guarded_prog    : '#' vopt GUARD prog
    '''

    p[0] = qast.AstGuardedProg(p[2], p[4])

    if p[0] is None:
        raise Exception()

def p_vopt(p):
    '''
    vopt   : ID qvar
    '''
    p[0] = qast.AstVOpt(p[1], p[2])

    if p[0] is None:
        raise Exception()

def p_qvar(p):
    '''
    qvar    : qvar_pre ']'
    '''

    p[0] = p[1]

    if p[0] is None:
        raise Exception()

def p_qvar_pre(p):
    '''
    qvar_pre    : '['
                | qvar_pre ID
    '''
    if p[1] == '[':
        p[0] = qast.AstQVar([])
    else:
        p[0] = p[1].appended(p[2])

    if p[0] is None:
        raise Exception()

def p_error(p):
    if p is None:
        raise Exception("unexpected end of file")
    raise Exception("Syntax error in input: '" + str(p.value) + "'. (" + str(p.lineno) + ", " + str(p.lexpos) + ")")


# Build the lexer
parser = yacc.yacc()