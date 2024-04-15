'''
    The calculation for quantum tree state
'''

from __future__ import annotations
from typing import List, Tuple, Dict


from .backend import *
from .flowchart.flowchart import *

from graphviz import Digraph

class Qts:
    '''
    quantum tree state
    '''
    qts_num = 0

    def __init__(self):
        self.id = Qts.qts_num
        Qts.qts_num += 1


    @staticmethod
    def bottom() -> Qts:
        return QtsRho(VMat.zeroMat())
    
    def opt_apply(self, vo : VSuperOpt | VMat) -> Qts:
        raise NotImplementedError()
    
    def show(self, output = "qts") -> None:
        '''
        output the quantum tree state in a diagram
        '''
        dot = Digraph()

        dot.node('-0', '', shape = 'none')
        dot.edge('-0', str(self.id))

        self._layout(dot)

        dot.render(output)


    def _layout(self, dot : Digraph) -> None:
        '''
        layout in a diagram
        '''
        raise NotImplementedError()
    
    def reduce(self) -> QtsRho | QtsNondet:
        '''
        return the reduced quantum tree state
        '''
        raise NotImplementedError()



class QtsRho(Qts):
    '''
        partial density operators : terminals of quantum tree states
    '''
    def __init__(self, _rho : VMat):
        super().__init__()
        self.rho = _rho

    def opt_apply(self, vo: VSuperOpt | VMat) -> Qts:
        if isinstance(vo, VSuperOpt):
            return QtsRho(self.rho.SOapply(vo))
        elif isinstance(vo, VMat):
            return QtsRho(vo.mul(self.rho, False).mul(vo.dagger()))
        else:
            raise Exception()
        
    def _layout(self, dot: Digraph) -> None:
        dot.node(str(self.id), str(self.rho), style = "filled",
                 shape = 'box', fontname = "Arial")

    def reduce(self) -> QtsRho | QtsNondet:
        return self


class QtsNondet(Qts):
    '''
        nondeterministic combination : connector for quantum tree states
    '''
    def __init__(self, _ls : List[Qts]):
        super().__init__()
        self.ls = _ls

    def opt_apply(self, vo: VSuperOpt | VMat) -> Qts:
        return QtsNondet([qts.opt_apply(vo) for qts in self.ls])
    
    def _layout(self, dot: Digraph) -> None:
        dot.node(str(self.id), '', shape = "square", width= '0.3',
                 style='filled, bold', fillcolor='lightyellow')

        for sub in self.ls:
            dot.edge(str(self.id), str(sub.id))
            sub._layout(dot)

    def reduce(self) -> QtsRho | QtsNondet:
        new_ls : List[QtsRho] = []
        for qts in self.ls:
            qts_r = qts.reduce()
            if isinstance(qts_r, QtsRho):
                new_ls.append(qts_r)
            else:
                new_ls = new_ls + qts_r.ls  # type: ignore

        # filter out repeated items
        res_ls : List[VMat] = []
        for qtsrho in new_ls:
            if qtsrho.rho not in res_ls:
                res_ls.append(qtsrho.rho)

        return QtsNondet([QtsRho(rho) for rho in res_ls])

class QtsProb(Qts):
    '''
        nondeterministic combination : connector for quantum tree states
    '''
    def __init__(self, _ls : List[Qts]):
        super().__init__()
        self.ls = _ls

    def opt_apply(self, vo: VSuperOpt | VMat) -> Qts:
        return QtsProb([qts.opt_apply(vo) for qts in self.ls])
    
    def _layout(self, dot: Digraph) -> None:
        dot.node(str(self.id), '', shape='circle', width= '0.3',
                 style='filled, bold', fillcolor='lightblue')

        for sub in self.ls:
            dot.edge(str(self.id), str(sub.id))
            sub._layout(dot)

    def reduce(self) -> QtsRho | QtsNondet:
        rho_ls = [VMat.zeroMat()]

        for qts in self.ls:
            qts_r = qts.reduce()
            if isinstance(qts_r, QtsRho):
                rho_ls = [rho + qts_r.rho for rho in rho_ls]
            elif isinstance(qts_r, QtsNondet):
                new_rho_ls = []
                for next_qts in qts_r.ls:
                    # we wiil guarantee that reduced qts is in the flat structure
                    if isinstance(next_qts, QtsRho):
                        new_rho_ls += [next_qts.rho + rho for rho in rho_ls]
                    else:
                        raise Exception()
                rho_ls = new_rho_ls
            else:
                raise Exception()
            
        # filter out repeated items
        res_ls : List[VMat] = []
        for rho in rho_ls:
            if rho not in res_ls:
                res_ls.append(rho)

        return QtsNondet([QtsRho(rho) for rho in res_ls])



# for qubit initialization
k0b0 = np.array([[1., 0.], [0., 0.]])
k0b1 = np.array([[0., 1.], [0., 0.]])


def qtscalc_iter(v : Vertex, qts : Qts, step_bound : int, optlib : OptEnv) -> Qts:
    '''
        iterative procedure for quantum tree state calculation
    '''
    if isinstance(v, TVertex):
        return qts
    
    if step_bound == 0:
        return Qts.bottom()
    
    else:
        if isinstance(v, PVertex):
            qts_ls : List[Qts] = []
            for e in v.outE:
                qts_ls.append(qtscalc_iter(e.B, qts, step_bound-1, optlib))
            return QtsNondet(qts_ls)
        
        if isinstance(v, MVertex):
            qts_ls : List[Qts] = []
            for e in v.outE:
                if not isinstance(e, MEdge):
                    raise Exception()
                mopt = mopt_eval(e.vopt, optlib)
                qts_ls.append(qtscalc_iter(e.B, qts.opt_apply(mopt), step_bound-1, optlib))
            return QtsProb(qts_ls)
        
        if len(v.outE) == 1:
            e = v.outE[0]
            if isinstance(e, UEdge):
                uopt = uopt_eval(e.vopt, optlib)
                return qtscalc_iter(e.B, qts.opt_apply(uopt), step_bound-1, optlib)
            
            if isinstance(e, AEdge):
                return Qts.bottom()
            
            if isinstance(e, IdEdge):
                return qtscalc_iter(e.B, qts, step_bound-1, optlib)
            
            if isinstance(e, InitEdge):
                # prepare all the initialization operators
                opt_ls = [VMat.idMat()]
                for q in e.qvar.ls:
                    opt_ls = [opt.mul(VMat(QVar([q]), k0b0)) for opt in opt_ls]\
                            + [opt.mul(VMat(QVar([q]), k0b1)) for opt in opt_ls]
                    
                return qtscalc_iter(e.B, 
                            qts.opt_apply(VSuperOpt(opt_ls)), 
                            step_bound-1, optlib)
            
        # if other situation happens 
        raise Exception()
    

def qtscalc(fc : Flowchart, rhoinit : VMat, step_bound = 30) -> Qts:
    '''
        calculate the quantum tree state approximation 
        within [step_bound] steps
    '''
    if not (VMat.zeroMat() <= rhoinit) or np.real(rhoinit.trace()) > 1 + rhoinit.eps:
        raise ValueError("Invalid partial density operator.")
    
    return qtscalc_iter(fc.vertices[0], QtsRho(rhoinit), step_bound, fc.optlib)

    
