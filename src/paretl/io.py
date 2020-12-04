import sys
import json


class JSONType:
    pass


class In:
    pass


class Out:

    def __init__(self, cls, Parameter, JSONType):
        self.parameterized = cls
        self.Parameter = Parameter
        self.JSONType = JSONType
        self._in = In()
        self.read_parameter_values(cls)

    def read_parameter_values(self, cls):
        # get default values
        for var in dir(self.parameterized):
            if var[0] == '_':
                continue
            try:
                val = getattr(self.parameterized, var)
            except Exception:
                continue
            if isinstance(val, self.Parameter):
                setattr(self, var, val.kwargs['default'])

        # get parameter values from cmd line
        args = sys.argv[2:]
        if len(args) > 0:
            if args[0] == "--help":
                print("")
                print('\033[92mRemember certain parameter choices will add new parameters!\033[0m')
                print("")
                args = args[1:]

            if len(sys.argv) < 2 or not (sys.argv[1] == 'run' or (len(sys.argv) > 3 and sys.argv[3] == 'run')):
                # read from (auto-) tags
                for a, b in zip(args[::2], args[1::2]):
                    if a == "--tag":
                        ls = b.split(':')
                        setattr(self, ls[0], ":".join(ls[1:]))
            else:
                # read from non tags
                for a, b in zip(args[::2], args[1::2]):
                    if a != "--tag":
                        setattr(self, a[2:], b)

        # register sweeps if any
        if hasattr(self, "sweep"):
            self.sweep = json.loads(self.sweep)
        elif hasattr(cls, "sweep"):
            self.sweep = json.loads(cls.sweep.kwargs['default'])

        # remove swept parameters but add first value
        if hasattr(self, "sweep"):
            for var, val in self.sweep.items():
                if hasattr(cls, var):
                    delattr(cls, var)
                setattr(self, var, val[0])

    def add_parameter(self, var, val):
        cls = self.parameterized

        # dependency injection of JSONType and Parameter
        if (val.type == JSONType):
            val.type = self.JSONType
        if not hasattr(cls, var) and (not hasattr(self, 'sweep') or var not in self.sweep):
            setattr(cls, var, val.as_injected(self.Parameter))

        # remove swept parameters but add first value
        if var == 'sweep':
            if hasattr(self, "sweep"):
                return
            self.sweep = json.loads(val.default)
            cls.sweep = val.as_injected(self.Parameter)
            for var, val in self.sweep.items():
                if hasattr(cls, var):
                    delattr(cls, var)
                setattr(self, var, val[0])
            return

        # keep parameter value as attribute
        if not hasattr(self, var):
            setattr(self, var, val.default)

        # keep parameter in _in
        setattr(self._in, var, val)


class TestIn:
    pass


class TestData:
    pass


class TestOut():

    def __init__(self, hide=[], logger=None):
        self.__dict__['data'] = TestData()
        self.__dict__['hide'] = hide
        if logger is None:
            def logger(k, v):
                print('o.%s' % k, '=', v)
        self.__dict__['logger'] = logger

    def add_parameter(self, var, val):
        if not hasattr(self, var):
            setattr(self, var, val.default)

    def __setattr__(self, k, v):
        if not k.startswith('_') and k not in self.hide:
            self.logger(k, v)
        self.__dict__[k] = v
        self.data.__dict__[k] = v
