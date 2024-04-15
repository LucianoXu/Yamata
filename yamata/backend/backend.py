# numpy calculation backend

from __future__ import annotations
from typing import List, Type, Tuple

import numpy as np


def ls_uniqueness_check(ls : List) -> bool:
    '''
    Checks whether all elements in the list are different from each other.
    '''
    for i in range(len(ls)):
        for j in range(i + 1, len(ls)):
            if ls[i] == ls[j]:
                return False
    return True

class QVar:
    def __init__(self, _ls : List[str]):
        if not ls_uniqueness_check(_ls):
            raise Exception()
        
        self.ls : List[str] = _ls

    def appended(self, id : str) -> QVar:
        return QVar(self.ls + [id])
    
    def __len__(self) -> int:
        return len(self.ls)
    
    def __add__(self, b : QVar) -> QVar:
        r = self.ls.copy()
        for i in b.ls:
            if i not in r:
                r.append(i)
        return QVar(r)
    
    def __str__(self):
        if len(self.ls) == 0:
            return '[]'
        
        r = '['
        for i in range(len(self.ls)-1):
            r += self.ls[i] + ' '
        r += self.ls[-1] + ']'
        return r
    
    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return self.ls == other.ls

    

    def perm_idx_to(self, qvar : QVar) -> Tuple[int]:
        '''
        The permutation from the current qvar to the desired qvar.
        '''
        r : List[int] = []
        for i in qvar.ls:
            r.append(self.ls.index(i))
        return tuple(r)



class VTerm:
    '''
    terms with quantum variables
    '''
    eps_value = 1e-10

    @property
    def eps(self) -> float:
        return self.eps_value

    def __init__(self, _qvar : QVar) -> None:
        self.qvar = _qvar

    @property
    def qnum(self) -> int:
        return len(self.qvar)

    def transform_to(self, tgt_qvar: QVar) -> VTerm:
        '''
        transform this term according to the target qvar and return the result
        '''
        raise NotImplementedError()
    
    def extend_to(self, tgt_qvar: QVar) -> VTerm:
        '''
        extend this term to contain the target qvar and return the result
        '''
        raise NotImplementedError()
        

class VVec(VTerm):
    def __init__(self, _qvar: QVar, _vec : np.ndarray) -> None:
        super().__init__(_qvar)

        # check dimension
        if len(_vec.shape) != 1:
            raise ValueError("Input is not a vector.")
        if 2**len(_qvar) != len(_vec):
            raise ValueError("Dimensions are not consistent.")
        
        self.vec = _vec
    
    def __str__(self) -> str:
        return str(self.qvar) + ":" + str(self.vec)

    def __eq__(self, other) -> bool:
        if not isinstance(other, VVec):
            return False
        
        return np.max(np.abs((self - other).vec)) < self.eps

    def transform_to(self, tgt_qvar: QVar) -> VVec:
        qvar_perm = list(self.qvar.perm_idx_to(tgt_qvar))

        new_v = self.vec.reshape((2,)*self.qnum).transpose(qvar_perm)
        new_v = new_v.reshape((2**len(tgt_qvar)))

        return VVec(tgt_qvar, new_v)


    def extend_to(self, tgt_qvar: QVar) -> VVec:
        appended_qvar = self.qvar + tgt_qvar
        
        # cylinder extension
        new_qubitn = len(tgt_qvar)-self.qnum
        # check whether extend is needed
        if new_qubitn == 0:
            return self.transform_to(tgt_qvar)

        else:
            new_v = self.vec.reshape((2,)*self.qnum)

            # WARNING : assume the default state is |0>
            appendix = np.zeros((2**new_qubitn,))
            appendix[0] = 1.
            appendix = appendix.reshape((2,)*new_qubitn)
            
            new_v = np.tensordot(new_v, appendix, 0).reshape((-1,))
            temp_v = VVec(appended_qvar, new_v)
        
            # permute
            return temp_v.transform_to(tgt_qvar)


    def __add__(self, vmat: VVec) -> VVec:
        common_qvar = self.qvar + vmat.qvar
        temp1 = self.extend_to(common_qvar)
        temp2 = vmat.extend_to(common_qvar)
        new_v = temp1.vec + temp2.vec
        return VVec(common_qvar, new_v)
    
    def __sub__(self, vmat: VVec) -> VVec:
        common_qvar = self.qvar + vmat.qvar
        temp1 = self.extend_to(common_qvar)
        temp2 = vmat.extend_to(common_qvar)
        new_v = temp1.vec - temp2.vec      # type: ignore
        return VVec(common_qvar, new_v)
    
    def Mapply(self, vmat : VMat) -> VVec:
        '''
            return the result of applying vmat on this vvec, in the qvar order of current vvec.
        '''
        common_qvar = self.qvar + vmat.qvar
        temp_v = self.extend_to(common_qvar)
        temp_m = vmat.extend_to(common_qvar)
        new_v = temp_m.mat @ temp_v.vec
        return VVec(common_qvar, new_v)
    
    def norm_vec(self) -> VVec:
        '''
            return the vector v^dagger * v, in real numbers
        '''
        norm_v = np.real(self.vec.conj() * self.vec)
        return VVec(self.qvar, norm_v)
    
    def norm2(self) -> float:
        '''
            return the square of the norm of this vector
        '''
        return sum(np.real(self.vec.conj() * self.vec))
    
    def normalized(self) -> VVec:
        '''
            return the normalized vector
        '''
        return VVec(self.qvar, self.vec / np.sqrt(self.norm2()))
    
    def outer(self) -> VMat:
        '''
            return the outproduct
        '''
        mat = np.tensordot(self.vec, self.vec.conj(), 0)
        return VMat(self.qvar, mat)
    
        
class VMat(VTerm):

    @staticmethod
    def idMat() -> VMat:
        return VMat(QVar([]), np.array([[1.]]))
    
    @staticmethod
    def zeroMat() -> VMat:
        return VMat(QVar([]), np.array([[0.]]))
    
    def __str__(self) -> str:
        r = str(self.qvar)+"\n"
        r += str(self.mat)
        return r

    def __init__(self, _qvar : QVar, _mat : np.ndarray) -> None:
        super().__init__(_qvar)

        # check dimension
        if len(_mat.shape) != 2:
            raise ValueError("Input is not a matrix.")
        expected_dim = 2**len(_qvar)
        if expected_dim != _mat.shape[0] or expected_dim != _mat.shape[1]:
            raise ValueError("Dimensions are not consistent.")

        self.mat = _mat

    def __eq__(self, other) -> bool:
        if not isinstance(other, VMat):
            return False
        
        return np.max(np.abs((self-other).mat)) < self.eps

    def transform_to(self, tgt_qvar: QVar) -> VMat:
        qvar_perm = list(self.qvar.perm_idx_to(tgt_qvar))

        # generate the new perm
        perm = qvar_perm.copy()
        for j in range(self.qnum):
            qvar_perm[j] += len(self.qvar)
        perm = perm + qvar_perm
        
        new_m = self.mat.reshape((2,)*2*self.qnum).transpose(perm)
        new_m = new_m.reshape((2**len(tgt_qvar), 2**len(tgt_qvar)))

        return VMat(tgt_qvar, new_m)


    def extend_to(self, tgt_qvar: QVar) -> VMat:
        appended_qvar = self.qvar + tgt_qvar
        
        # cylinder extension
        new_qubitn = len(tgt_qvar)-self.qnum
        # check whether extend is needed
        if new_qubitn == 0:
            return self.transform_to(tgt_qvar)

        else:
            new_m = self.mat.reshape((2,)*2*self.qnum)

            appendix = np.identity(2**new_qubitn).reshape((2,)*new_qubitn*2)
            new_m = np.tensordot(new_m, appendix, 0)
            temp_perm = []
            
            temp_perm += list(range(self.qnum))
            temp_perm += list(range(2*self.qnum, 2*self.qnum + new_qubitn))
            temp_perm += list(range(self.qnum, 2 * self.qnum))
            temp_perm += list(range(2*self.qnum + new_qubitn, 2*self.qnum + 2*new_qubitn))
            
            new_m = new_m.transpose(temp_perm).reshape((2**len(tgt_qvar), 2**len(tgt_qvar)))

            temp_m = VMat(appended_qvar, new_m)
        
            # permute
            return temp_m.transform_to(tgt_qvar)


    def dagger(self) -> VMat:
        return VMat(self.qvar, self.mat.conjugate().transpose())

    def mul(self, vmat: VMat, self_order = True) -> VMat:
        '''
        self_order : if set to False, will try to order the variables
            according to [vmat]
        '''
        if self_order:
            common_qvar = self.qvar + vmat.qvar
        else:
            common_qvar = vmat.qvar + self.qvar

        temp1 = self.extend_to(common_qvar)
        temp2 = vmat.extend_to(common_qvar)
        new_mat = temp1.mat @ temp2.mat
        return VMat(common_qvar, new_mat)
    
    def trace(self) -> float:
        return np.trace(self.mat)
        
    def __add__(self, vmat: VMat) -> VMat:
        common_qvar = self.qvar + vmat.qvar
        temp1 = self.extend_to(common_qvar)
        temp2 = vmat.extend_to(common_qvar)
        new_m = temp1.mat + temp2.mat
        return VMat(common_qvar, new_m)
    
    def __sub__(self, vmat: VMat) -> VMat:
        common_qvar = self.qvar + vmat.qvar
        temp1 = self.extend_to(common_qvar)
        temp2 = vmat.extend_to(common_qvar)
        new_m = temp1.mat - temp2.mat      # type: ignore
        return VMat(common_qvar, new_m)
    
    def __le__(self, b : VMat) -> bool:
        common_qvar = self.qvar + b.qvar
        extendedself = self.extend_to(common_qvar)
        extendedb = b.extend_to(common_qvar)

        diff : np.ndarray = extendedb.mat - extendedself.mat  # type: ignore
        eig_vals = np.linalg.eigvals(diff)
        return bool(np.min(eig_vals) > -self.eps)
    
    def SOapply(self, vso : VSuperOpt) -> VMat:
        opt_sum = VMat.zeroMat()
        for vopt in vso.ls:
            opt_sum = opt_sum + vopt.mul(self, False).mul(vopt.dagger())
        return opt_sum



class VSuperOpt(VTerm):
    def __init__(self, _ls : List[VMat]):
        self.ls = _ls