
from __future__ import annotations
from typing import List

from ..qast import AstQVar, AstVOpt
from ..backend import *

def qvar_backend(qvar : AstQVar) -> QVar:
    return QVar(qvar.ls)

def uopt_eval(vopt : AstVOpt, optlib : OptEnv) -> VMat:
    return VMat(qvar_backend(vopt.qvar), optlib.unitary_opt[vopt.opt_id])

def mopt_eval(vopt : AstVOpt, optlib : OptEnv) -> VMat:
    return VMat(qvar_backend(vopt.qvar), optlib.measure_opt[vopt.opt_id])