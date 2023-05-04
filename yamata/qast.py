'''

    The abstract syntax tree for 

        parallel quantum programs  in YAMATA

        
'''





from __future__ import annotations
from typing import List


def ls_uniqueness_check(ls : List) -> bool:
    '''
    Checks whether all elements in the list are different from each other.
    '''
    for i in range(len(ls)):
        for j in range(i + 1, len(ls)):
            if ls[i] == ls[j]:
                return False
    return True

class AstQVar:
    def __init__(self, _ls : List[str]):
        if not ls_uniqueness_check(_ls):
            raise Exception()
        
        self.ls : List[str] = _ls

    def appended(self, id : str) -> AstQVar:
        return AstQVar(self.ls + [id])
    
    def __str__(self):
        r = '['
        for i in range(len(self.ls)-1):
            r += self.ls[i] + ' '
        r += self.ls[-1] + ']'
        return r
    
    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return self.ls == other.ls

class AstVOpt:
    def __init__(self, _opt_id : str, _qvar : AstQVar):
        self.opt_id = _opt_id
        self.qvar = _qvar
    
    def __str__(self):
        return self.opt_id + str(self.qvar)
    
    def __eq__(self, other):
        if type(self) != type(other):
            return False

        return self.opt_id == other.opt_id and self.qvar == other.qvar

class AstGuardedProg:
    def __init__(self, _vopt : AstVOpt, _prog : AstStatement):
        self.vopt = _vopt
        self.prog = _prog

    def to_str_prefix(self, pre: str) -> str:
        r = pre + '# ' + str(self.vopt) + ' ' + '->' + '\n' \
            + self.prog.to_str_prefix(pre + "  ") + "\n"
        return r
    
    def __eq__(self, other):
        if type(self) != type(other):
            return False

        return self.vopt == other.vopt and self.prog == other.prog


# Abstract syntax tree for programs
class AstStatement:
    def to_str_prefix(self, pre : str) -> str:
        raise NotImplementedError()
    
    def __str__(self):
        return self.to_str_prefix("")
    
    def first(self) -> AstStatement:
        '''
            return the first piece of program statement
        '''
        if isinstance(self, AstSeq):
            return self.S0.first()
        else:
            return self
        
    def __eq__(self, other):
        raise NotImplementedError()


class AstTerminal(AstStatement):
    def __init__(self):
        pass

    def __str__(self):
        return "↓"
    
    def __eq__(self, other):
        return isinstance(other, AstTerminal)


class AstSeq(AstStatement):
    def __init__(self, _S0 : AstStatement, _S1 : AstStatement):
        '''
            This constructor will convert any combination to the 
            right associative canonical form.
        '''
        temp_S0 = _S0
        temp_S1 = _S1
        while isinstance(temp_S0, AstSeq):
            temp_S1 = AstSeq(temp_S0.S1, temp_S1)
            temp_S0 = temp_S0.S0
        self.S0 = temp_S0
        self.S1 = temp_S1
    
    def to_str_prefix(self, pre : str) -> str:
        r = self.S0.to_str_prefix(pre) + ";\n" + self.S1.to_str_prefix(pre)
        return r
    
    def __eq__(self, other):
        if not isinstance(other, AstSeq):
            return False

        return self.S0 == other.S0 and self.S1 == other.S1


class AstSkip(AstStatement):
    def to_str_prefix(self, pre: str) -> str:
        return pre + 'skip'
    
    def __eq__(self, other):
        if not isinstance(other, AstSkip):
            return False

        return isinstance(other, AstSkip)

class AstAbort(AstStatement):
    def to_str_prefix(self, pre: str) -> str:
        return pre + 'abort'
    
    def __eq__(self, other):
        if not isinstance(other, AstAbort):
            return False

        return isinstance(other, AstAbort)

class AstInit(AstStatement):
    def __init__(self, _qvar : AstQVar):
        self.qvar = _qvar

    def to_str_prefix(self, pre: str) -> str:
        return pre + str(self.qvar) + ' ' + ':=0'
    
    def __eq__(self, other):
        if not isinstance(other, AstInit):
            return False

        return self.qvar == other.qvar

class AstUnitary(AstStatement):
    def __init__(self, _vopt : AstVOpt):
        self.vopt = _vopt

    def to_str_prefix(self, pre: str) -> str:
        return pre + str(self.vopt)
    
    def __eq__(self, other):
        if not isinstance(other, AstUnitary):
            return False

        return self.vopt == other.vopt

class AstIf(AstStatement):
    def __init__(self, _ls : List[AstGuardedProg]):
        self.ls = _ls

    def to_str_prefix(self, pre: str) -> str:
        r = pre + "if \n"
        for item in self.ls:
            r += item.to_str_prefix(pre + "  ")
        r += pre + "end"
        return r
    
    def __eq__(self, other):
        if not isinstance(other, AstIf):
            return False

        return self.ls == other.ls

class AstWhile(AstStatement):
    def __init__(self, _body : AstGuardedProg, _term_vopt):
        self.body = _body
        self.term_vopt = _term_vopt

    def to_str_prefix(self, pre: str) -> str:
        r = pre + "while \n"
        r += self.body.to_str_prefix(pre + "  ")
        r += pre + "  " + '# ' + str(self.term_vopt) + ' ' + '->' + " end"
        return r
    
    def __eq__(self, other):
        if not isinstance(other, AstWhile):
            return False

        return self.body == other.body and self.term_vopt == other.term_vopt
        

class AstParallel(AstStatement):
    def __init__(self, _ls : List[AstStatement]):
        self.ls = _ls
    def appended(self, seq : AstStatement) -> AstParallel:
        return AstParallel(self.ls + [seq])
    
    def to_str_prefix(self, pre : str) -> str:
        r = pre + "[ \n"
        for i in range(0, len(self.ls) - 1):
            r += self.ls[i].to_str_prefix(pre + "  ") + " ||\n"
        r += self.ls[-1].to_str_prefix(pre + "  ") + "\n"
        r += pre + "]"
        return r
    
    def __eq__(self, other):
        if not isinstance(other, AstParallel):
            return False

        return self.ls == other.ls
    
    def remove(self, i) -> AstStatement:
        '''
            remove the parallel component and return the resulting new program
        '''
        new_ls = self.ls[:i] + self.ls[i+1:]
        if len(new_ls) == 1:
            return new_ls[0]
        return AstParallel(new_ls)
