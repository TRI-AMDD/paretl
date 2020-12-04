class Result:

    def __init__(self, kv={}):
        self.__dict__.update(kv)

    def __repr__(self):
        return self.__dict__.__repr__()

    def as_dict(self):
        return dict(self.__dict__)


class Sweep:

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


class Swept:

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
