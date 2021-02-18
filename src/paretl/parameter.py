from .io import In, Out
import sys


class Is(list):
    pass


class Parameter:

    type = None
    custom = []

    def __init__(self, name, **kwargs):
        self.name = name
        self.__dict__.update(kwargs)

    def as_injected(self, injected_type):
        d = {k: v for k, v in self.__dict__.items() if k != 'custom'}
        return injected_type(**d)


class Parameterized:

    factories = {}

    def __init__(self, **kwargs):
        self.parameterize()
        self.add_parameter_tags()
        self.sweep_index = 0
        super().__init__(**kwargs)

    def process(self, i):
        if isinstance(i, list):
            i = Is(i)
            for io in i:

                from .util import timeit
                # TODO make it right
                io[1].add_parameter = lambda i, o: 0
                io[1].timeit = timeit
                #lambda a, b, c, d, e: 0

                io.append(self.factories["get_etl"](io[0], io[1]))
        print('\033[94mDo ETL %s\033[0m' % str(i))
        self.factories["get_etl"](i, self).etl(i, self)

    def parameterize(self):
        cls = self.__class__
        get_etl = self.factories["get_etl"]
        cls.factories = {"get_etl": get_etl}

        if hasattr(self, 'doc'):
            info = self.doc
            cls.__doc__ += '\033[92m%s\033[0m' % info

        # create out for adding parameters
        out = Out(cls, self._Parameter, self._JSONType)

        # fetch and add parameters recursively
        cls.etl = get_etl(In(), out)

        # add custom parameters for sweep cases
        if hasattr(out, "sweep"):
            for var, v in out.sweep.items():
                for val in v:
                    if val in getattr(out._in, var).custom:
                        # fetch again with custom value
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
