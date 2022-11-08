"""Classes for input and output objects used for passing along state and gathering output in ETLs.

"""


class In:
    """
    Base class for intermediate-state-passing dubbed input, in or i.

    """
    id = ''
    pass


class Out:
    """
    Base class for final-state-passing and output gathering dubbed output, out or o.

    """
    pass


class DebugIn(In):
    """Input class for debugging that does nothing.

    """
    def __init__(self):
        """
        Add data attribute.
        """
        self.__dict__['data'] = In()
        super().__init__()

    def __setattr__(self, k, v):
        self.__dict__[k] = v
        self.data.__dict__[k] = v


class DebugOut(Out):
    """Output class for debugging that simply stores and logs output.

    """

    def __init__(self, hide=[], logger=lambda k, v: print('o.%s ' % k, '=', v), include=None, parameters={}):
        """

        Args:
            hide (list) names of attributes to hide from logging
            logger (lambda k,v) called when an attribute is set
        """
        self.data = Out()
        self._hide = hide
        self._logger = logger
        self._include = include
        self._parameters = parameters
        super().__init__()

    def add_parameter(self, var, val):
        """Mehod to add parameter

        Args:
            var (string) parameter name
            val (Parameter) parameter object
        """
        self._parameters[var] = val
        if not hasattr(self, var):
            setattr(self, var, val.default)

    def __setattr__(self, k, v):
        """

        Args:
            k (string): name
            v (object): value
        """
        if k in ['data'] or k.startswith('_'):
            self.__dict__[k] = v
            return

        if self._include is not None:
            if k in self._include:
                self._logger(k, v)
        elif k not in self._hide:
            self._logger(k, v)
        self.__dict__[k] = v
        self.data.__dict__[k] = v
