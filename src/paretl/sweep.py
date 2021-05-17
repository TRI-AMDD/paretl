"""Classes related to parameter sweeps.

"""


class Result:
    """
    Base class for a result of a parameter sweep.

    """
    def __init__(self, kv={}):
        self.__dict__.update(kv)

    def __repr__(self):
        return self.__dict__.__repr__()

    def as_dict(self):
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
        self.key = key
        self.i = i
        self.o = o
        self.ires = {}
        self.ores = {}

    def add(self, value):
        ires = self.ires[value] = Result({self.key: value})
        ores = self.ores[value] = Result({self.key: value})
        i = Swept(self.i, ires)
        o = Swept(self.o, ores)
        return i, o

    def load(self):
        setattr(self.o, "%s_sweep" % self.key, {k: v.as_dict() for k, v in self.ores.items()})
        return self.i, self.o

    def load_io(self):
        setattr(self.i, "%s_sweep" % self.key, {k: v.as_dict() for k, v in self.ires.items()})
        setattr(self.o, "%s_sweep" % self.key, {k: v.as_dict() for k, v in self.ores.items()})
        return self.i, self.o


class Swept:
    """
    Base class decorating input and output with their swept dittos.

    Attributes:
        parent (object) the undecorated input or output, or the as swept in the parent sweep
        result (object) the result object to load into
    """

    def __init__(self, parent, result):
        self.__dict__["parent"] = parent
        self.__dict__["result"] = result

    def __setattr__(self, key, value):
        self.__dict__[key] = value
        setattr(self.result, key, value)

    def __getattr__(self, key):
        if key in self.__dict__:
            return self.__dict__[key]
        elif hasattr(self.result, key):
            return getattr(self.result, key)
        else:
            return getattr(self.parent, key)
