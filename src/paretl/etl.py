import sys
import time
import json


class TestIn:
    pass


class TestData:
    pass


class TestOut():

    def __init__(self, hide=[]):
        self.__dict__['data'] = TestData()
        self.__dict__['hide'] = hide

    def add_parameter(self, var, val):
        if not hasattr(self, var):
            setattr(self, var, val.kwargs['default'])

    def __setattr__(self, k, v):
        if not k.startswith('_') and not k in self.hide:
            print('o.%s' % k, '=', v)
        self.__dict__[k] = v
        self.data.__dict__[k] = v


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
            except:
                continue
            if isinstance(val, self.Parameter):
                setattr(self, var, val.kwargs['default'])

        # get parameter values from cmd
        args = sys.argv[2:]
        if len(args) > 0:
            if args[0] == "--help":
                print("")
                print('\033[92mRemember certain parameter choices will add new parameters!\033[0m')
                print("")
                args = args[1:]

            if len(sys.argv) < 2 or not (sys.argv[1] == 'run' or (len(sys.argv) > 3 and sys.argv[3] == 'run')):
                for a, b in zip(args[::2], args[1::2]):
                    if a == "--tag": # and a[2:]:
                        l = b.split(':')
                        setattr(self, l[0], ":".join(l[1:]))
            else:
                for a, b in zip(args[::2], args[1::2]):
                    if a != "--tag": # and a[2:]:
                        setattr(self, a[2:], b)

        # register sweeps if any
        if hasattr(self, "sweep"):
            self.sweep = json.loads(self.sweep)
        elif hasattr(cls, "sweep"):
            self.sweep = json.loads(cls.sweep.kwargs['default'])

        if hasattr(self, "sweep"):
            for var, val in self.sweep.items():
                if hasattr(cls, var):
                    delattr(cls, var)
                setattr(self, var, val[0])

    def add_parameter(self, var, val):
        cls = self.parameterized
        if ('type' in val.kwargs and val.kwargs['type'] == JSONType):
            val.kwargs['type'] = self.JSONType
        if not hasattr(cls, var) and (not hasattr(self, 'sweep') or var not in self.sweep):
            setattr(cls, var, self.Parameter(var, **val.kwargs))
        if var == 'sweep':
            if hasattr(self, "sweep"):
                return
            self.sweep = json.loads(val.kwargs['default'])
            cls.sweep = self.Parameter('sweep', **val.kwargs)
            for var, val in self.sweep.items():
                if hasattr(cls, var):
                    delattr(cls, var)
                setattr(self, var, val[0])
            return
        # with dependency injections: Parameter, JSONType
        if not hasattr(self, var):
            setattr(self, var, val.kwargs['default'])
        setattr(self._in, var, val)


class Parameter:

    def __init__(self, name, custom=[], sweep=None, **kwargs):
        self.kwargs = kwargs
        self.custom = custom
        self.sweep = sweep


class JSONType:
    pass


class ETL:

    def __init__(self, i, o):
        self.i = i
        self.o = o
        if hasattr(o, 'add_parameter'):
            self._add_parameters(i, o)

    def _add_parameters(self, i, o):
        for var, val in self._get_parameters():
            if hasattr(o, 'add_parameter'):
                o.add_parameter(var, val)

    def _get_parameters(self):
        for var in dir(self):
            if var[0] == '_':
                continue
            try:
                val = getattr(self, var)
            except:
                continue
            if isinstance(val, Parameter):
                yield var, val

    def etl(self, i, o):
        self.extract(i, o)
        self.transform(i, o)
        self.load(i, o)

    def et(self, i, o):
        self.extract(i, o)
        self.transform(i, o)

    def tl(self, i, o):
        self.transform(i, o)
        self.load(i, o)

    def extract(self, i, o):
        pass

    def transform(self, i, o):
        pass

    def load(self, i, o):
        pass


class Parameterized:

    factories = {}

    def __init__(self, **kwargs):
        #parameterize(self.__class__, self.factories['get_etl'], self.__doc__, self.__class__)
        self.parameterize()
        self.add_parameter_tags()
        self.sweep_index = 0
        super().__init__(**kwargs)

    def process(self, i):
        print(f'\033[94mDo ETL {i}\033[0m {self.pipeline}')
        self.factories["get_etl"](i, self).etl(i, self)
        # self.etl.etl(i, self)

    def parameterize(self):
        cls = self.__class__
        get_etl = self.factories["get_etl"]
        info = self.doc
        cls.__doc__ += f'\033[92m{info}\033[0m'
        # print(sys.argv)
        # if len(sys.argv) < 2 or not (sys.argv[1] == 'run' or (len(sys.argv) > 3 and sys.argv[3] == 'run')):
            # return cls
        out = Out(cls, self._Parameter, self._JSONType)
        cls.etl = get_etl(In(), out)
        cls.factories = {"get_etl": get_etl}
        # add parameters for sweep cases
        if hasattr(out, "sweep"):
            for var, v in out.sweep.items():
                for val in v:
                    if val in getattr(out._in, var).custom:
                        setattr(out, var, val)
                        get_etl(In(), out)
        return cls

    def add_parameter_tags(self):
        if len(sys.argv) > 1 and (sys.argv[1] == 'run' or (len(sys.argv) > 3 and sys.argv[3] == 'run')):
            excl = ['ep', 'environment', 'metadata', 'datastore', 'run-id',
                    'task-id', 'event-logger', 'monitor', 'datastore-root', 'input-paths']
            done = {}
            args = sys.argv[2:]

            for a, b in zip(args[::2], args[1::2]):
                if a != "--tag" and a[2:] not in excl:
                    sys.argv.extend(["--tag", a[2:] + ':' + b])
                    done[a[2:]] = True
            for k, v in self._get_parameters():
                if k in done:
                    continue
                sys.argv.extend(["--tag", "%s:%s" % (k, str(v.kwargs['default']))])


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
        setattr(self.o, f"{self.key}_sweep", {k: v.as_dict() for k, v in self.ores.items()})
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


def tim(method):
    def tm(*args, **kwargs):
        slf = args[0]
        if hasattr(slf.o, "timeit"):
            slf.o.timeit(method, slf.o, *args, **kwargs)
        else:
            method(*args, **kwargs)
    return tm


def timeit(method, o, *args, **kw):
    ts = time.time()
    result = method(*args, **kw)
    te = time.time()
    if 'log_time' in kw:
        name = kw.get('log_name', method.__name__.upper())
        kw['log_time'][name] = int((te - ts) * 1000)
    else:
        setattr(o, 'ms_%s_%s' % (type(args[0]).__name__, method.__name__),  (te - ts) * 1000)
    return result
