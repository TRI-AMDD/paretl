"""Classes related to parameter sweeps.

"""


class Result:
    """
    Base class for a result of a parameter sweep.

    """
    def __init__(self, kv={}):
        """

        Arguments:
            kv (dict) initial results
        """
        self.__dict__.update(kv)

    def as_dict(self):
        """
        Method to represent the result as a dict

        Returns:
            the resul as a dict
        """
        return dict(self.__dict__)


class Sweep:
    """
    Base class for a parameter sweep.

    Attributes:
        i (object) the undecorated input
        o (object) the undecorated input
        ires (object) the input result
        ores (object) the output result
    """

    def __init__(self, key, i, o):
        """

        Arguments:
            key (string) name of parameter being swept
            i (object) the input
            o (object) the output
        """
        self.key = key
        self.i = i
        self.o = o
        self.ires = {}
        self.ores = {}

    def add(self, value):
        """
        Method to add a parameter value case to the sweep

        Arguments:
            value (object) the parameter value

        Returns:
            dedicated swept input and output objects to be used in the ETL for this case
        """
        ires = self.ires[value] = Result({self.key: value})
        ores = self.ores[value] = Result({self.key: value})
        i = Swept(self.i, ires)
        o = Swept(self.o, ores)
        return i, o

    def load(self):
        """
        Method to load the swept output result of the sweep into the parent output

        Returns:
            the parent input and output objects
        """
        setattr(self.o, "%s_sweep" % self.key, {k: v.as_dict() for k, v in self.ores.items()})
        return self.i, self.o

    def load_io(self):
        """
        Method to load both the swept input and output result of the sweep into the parent input and output respectively

        Returns:
            the parent input and output objects
        """
        setattr(self.i, "%s_sweep" % self.key, {k: v.as_dict() for k, v in self.ires.items()})
        setattr(self.o, "%s_sweep" % self.key, {k: v.as_dict() for k, v in self.ores.items()})
        return self.i, self.o


class Swept:
    """
    Base class decorating input and output with their swept dittos to be used in ETLs for a case in a parameter sweep.

    Attributes:
        parent (object) the parent input or output
        result (object) the result for gathering results
    """

    def __init__(self, parent, result):
        """

        Arguments:
            parent (object) the parent input or output
            result (Result) the result object for gathering results
        """
        self.__dict__["parent"] = parent
        self.__dict__["result"] = result

    def __setattr__(self, key, value):
        # set attribute both in self and result
        self.__dict__[key] = value
        setattr(self.result, key, value)

    def __getattr__(self, key):
        # get attribute from self, result or parent
        if hasattr(self.result, key):
            return getattr(self.result, key)
        else:
            return getattr(self.parent, key)
