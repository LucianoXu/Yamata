
# ------------------------------------------------------------
# vlexer.py
#
# tokenizer
# ------------------------------------------------------------

from __future__ import annotations
from typing import Any, List

import ply.lex as lex

reserved = {
    # for programs and verifications
    'skip'  : 'SKIP',
    'abort' : 'ABORT',
    'if'    : 'IF',
    'while' : 'WHILE',
    'end'   : 'END',
    'loop'  : 'LOOP',
}

# List of token names.
tokens = [
    'ID',
    'INIT',
    'GUARD',
    'PARALLEL',
 ] + list(reserved.values())

# Regular expression rules for simple tokens
t_INIT = r':=0'
t_GUARD = r'->'
t_PARALLEL = r'\|\|'

literals = [';', '[', ']', '#', '<', '>', '{', '}']


# use // or /* */ to comment
def t_COMMENT(t):
    r'(/\*(.|\n)*?\*/)|(//.*)'
    for c in t.value:
        if c == '\n':
            t.lexer.lineno += 1

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value,'ID')    # Check for reserved words
    return t

# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


# A string containing ignored characters (spaces and tabs)
t_ignore = ' \t'


def t_error(t):
    raise Exception("Syntax Error. Illegal character '" + t.value[0] + "'.")


# Build the lexer
lexer = lex.lex()