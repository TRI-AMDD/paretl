"""Minimalistic python package for doing parameterized Extract-Transform-Load\
     in state-passing style with support for nested parameter sweeps."""
__version__ = '0.3.0'

from .io import DebugIn, DebugOut, In, Out
from .etl import *
from .parameter import Parameter, Parameterized, ParameterizingOut, Parameters, JSONType, Inputs
from .sweep import *
from .util import *


def get_io():
    """Factory for debug io"""
    return DebugIn(), DebugOut(parameters=Parameters())
