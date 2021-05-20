"""Classes for input and output objects used for passing along state and gathering output in ETLs.

"""


class In:
    """
    Base class for intermediate-state-passing dubbed input, in or i.

    """
    pass


class Out:
    """
    Base class for final-state-passing and output gathering dubbed output, out or o.

    """
    pass


class DebugIn(In):
    """Input class for debugging that does nothing.

    """
    pass


class DebugOut(Out):
    """Output class for debugging that simply stores and logs output.

    """

    def __init__(self, hide=[], logger=lambda k, v: print('o.%s ' % k, '=', v)):
        """

        Arguments:
            hide (list) names of attributes to hide from logging
            logger (lambda k,v) called when an attribute is set
        """
        self.__dict__['data'] = Out()
        self.__dict__['hide'] = hide
        self.__dict__['logger'] = logger
        super().__init__()

    def add_parameter(self, var, val):
        if not hasattr(self, var):
            setattr(self, var, val.default)

    def __setattr__(self, k, v):
        if not k.startswith('_') and k not in self.hide:
            self.logger(k, v)
        self.__dict__[k] = v
        self.data.__dict__[k] = v
