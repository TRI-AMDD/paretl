"""Classes related to parameterizing ETLs.

"""
from .io import In, Out
from .util import timeit
import sys
import json


class Parameter:
    """
    Base class for a parameter.

    Attributes:
        name (string) parameter name
        default (string) default value
        type (string or JSONType) type of parameter value
        custom (list) list of parameter choices that will add custom parameters
        kwargs (dict) keyword arguments supplied at initialization
    """

    type = None
    custom = []

    def __init__(self, name, **kwargs):
        """

        Args:
            name (string): parameter name
            default (string) default value
            type (string or the value JSONType) type of parameter value
            custom (list) list of parameter choices that will add custom parameters
        """
        self.name = name
        self.__dict__.update(kwargs)
        self.kwargs = kwargs

    def as_injected(self, injected_type):
        """
        Method to cast this parameter as dependency injected type

        Args:
            injected_type (type) type to cast to
        """

        # collect attributes without custom
        d = {k: v for k, v in self.__dict__.items() if k != 'custom'}

        # create and return
        return injected_type(**d)


class ParameterizingOut(Out):
    """
    Class used at initialization of a parameterized object to gather parameters from its ETL and make them concrete.
    Order of parameter value precedence: cmd-line overrides > script defaults > ETL defaults.

    Attributes:
        parameterized (class): the parameterized script object with an ETL factory
        Parameter (class): the dependency injected Parameter type
        JSONType (class): the dependency injected JSONType type

    Private Attributes:
        _in (object): the intermediate state
    """

    def __init__(self, cls, Parameter, JSONType):
        self.parameterized = cls
        self.Parameter = Parameter
        self.JSONType = JSONType
        self._in = In()

    def read_parameter_values(self, args=sys.argv[2:]):
        self.read_parameter_defaults()
        self.read_parameter_overrides(args)
        self.parse_sweep()

    def read_parameter_defaults(self):
        """
        Method to read default parameter values from parameterized class into this output

        """

        # get default paremter values from parameterized class
        for var in dir(self.parameterized):
            if var[0] == '_':
                continue
            # try:
            val = getattr(self.parameterized, var)
            # except Exception:
            #     continue
            if isinstance(val, self.Parameter):
                setattr(self, var, val.kwargs['default'])

    def read_parameter_overrides(self, args=sys.argv[2:]):
        """
        Method to read overridden parameters from command line arguments

        Args:
            args (string) command line arguments
        """

        # get parameter value overrides from cmd line
        if len(args) > 0:
            if args[0] == "--help":
                print("")
                print('\033[92mRemember certain parameter choices will add new parameters!\033[0m')
                print("")
                args = args[1:]

            if not (args[1] == 'run' or (len(args) > 1 and args[0] == 'run')):
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

    def parse_sweep(self, sweep_json=None):
        """
        Method parse sweep parameter from json

        Args:
            sweep_json (string) the json representation of the sweep dic
        """
        if sweep_json is None:
            sweep_json = getattr(self, 'sweep', '{}')
        self.sweep = json.loads(sweep_json)

        # remove swept parameters but add first value
        for name, vals in self.sweep.items():
            # remove parameter from class
            if hasattr(self.parameterized, name):
                setattr(self.parameterized, name, "swept")
            # add first value in sweep to this output
            setattr(self, name, vals[0])

    def add_parameter(self, name, param):
        """
        Method to add a parameter to the parameterized class

        Args:
            name (string) name of parameter
            param (object) abstract parameter
        """

        # parameterized class
        cls = self.parameterized

        # dependency injection of JSONType
        if (param.type == JSONType):
            param.type = self.JSONType

        # only add parameter if it's new and not part of a sweep
        if not hasattr(cls, name) and (not hasattr(self, 'sweep') or name not in self.sweep):

            # add parameter to cls using dependency injected Parameter type
            setattr(cls, name, param.as_injected(self.Parameter))

        # handle parameter sweep
        if name == 'sweep':

            # we already have a sweep - do it only once
            if hasattr(self, "sweep"):
                return

            # parse sweep into dict
            self.parse_sweep(param.default)
        else:
            # keep parameter default param as attribute
            if not hasattr(self, name):
                setattr(self, name, param.default)

            # keep parameter in _in
            setattr(self._in, name, param)


class Parameterized:
    """
    Mixin class for parameterizing an object using its ETL.

    Assertions about mixer:
        - has attribute factories (dict) with a factories["get_etl"] factory for creating an ETL object
        - injects dependencies for implementing Parameter and JSONType via _Parameter and _JSONType attributes

    Attributes:
        sweep_index (int): Current index for parameter sweeps.
        _Parameter (type): dependency injected class for parameters
        _JSONType (type): dependency injected class for JSON parameter values
    """
    factories = {}
    doc = "A parameterized script"

    def __init__(self, **kwargs):
        self.parameterize()
        self.add_parameter_tags()
        self.sweep_index = 0
        super().__init__(**kwargs)

    def parameterize(self):
        """Method to recursively add any parameters from the ETL.

        Returns: the class for convenience
        """
        # modifications will happen to the class
        cls = self.__class__

        # the factory for creating the ETL object
        get_etl = self.factories["get_etl"]

        # create own factories dict
        cls.factories = {"get_etl": get_etl}

        # create own doc string
        cls.__doc__ = '\033[92m%s\033[0m' % self.doc

        # here we just need a foo input object
        i = In()

        # create out for adding parameters while using dependency injections for Parameter and JSONType classes
        o = ParameterizingOut(cls, self._Parameter, self._JSONType)

        # read parameter values using cls itself
        o.read_parameter_values()

        # add additional parameters recursively by simply creating the ETL object
        cls.etl = get_etl(i, o)

        # add any custom parameters for all parameter sweep cases
        for var, vals in o.sweep.items():
            for val in vals:
                if val in getattr(o._in, var).custom:
                    # fetch again with custom value
                    setattr(o, var, val)
                    get_etl(i, o)
        return cls

    def add_parameter_tags(self, tag="--tag", fmt="%s:%s", ignore=[
                'ep', 'environment', 'metadata', 'datastore', 'run-id',
                'task-id', 'event-logger', 'monitor', 'datastore-root', 'input-paths'], args=sys.argv):
        """
        Method to add parameters and their values as command line arguments e.g. in the form: --tag var:val
        The primary use case is for auto-tagging metaflow runs.

        Arguments:
        tag (str) command line argument string
        fmt (str) format for parameter name and value e.g. "%s:%s" for var:val
        ignore (list) names of command line arguments to ignore when auto-tagging
        """

        # only add tags if we run the metaflow
        if len(args) > 1 and (args[1] == 'run' or (len(args) > 3 and args[3] == 'run')):
            done = {}
            oargs = args[2:]

            # add parameters overrides from the command line arguments
            for a, b in zip(oargs[::2], oargs[1::2]):
                if a != tag and a[2:] not in ignore:
                    args.extend([tag, fmt % (a[2:], b)])
                    done[a[2:]] = True

            # add the rest of the parameters from the class itself
            for k, v in self._get_parameters():
                # skip if overridden
                if k in done:
                    continue
                # otherwise use default value
                args.extend([tag, fmt % (k, str(v.kwargs['default']))])

    def process(self, i):
        """
        Method to process a single input or a list of [i,o] pairs

        Arguments:
            i (object) a single input or a list of [i,o] pairs
        """

        # the ETL factory
        get_etl = self.factories["get_etl"]

        if isinstance(i, list):
            # decorate list with Inputs
            i = Inputs(i)

            # process i,o pairs
            for io in i:
                _i, o = io

                # TODO make it right
                # ignore parameters
                o.add_parameter = lambda i, o: 0
                o.timeit = timeit

                # create and append ETL object to list [i,o] -> [i,o,etl]
                io.append(get_etl(_i, o))

        # simple logging - TODO make it right
        print('\033[94mDo ETL %s\033[0m' % str(i))

        # create ETL and execute it using self as output
        o = self
        get_etl(i, o).etl(i, o)

    def _get_parameters(self):
        """Provide own parameters as a generator of name,value pairs.

        """
        # go through attributes by name
        for name in dir(self):
            # skip private
            if name[0] == '_':
                continue

            # make sure it is accessible and get attribute value
            # try:
            value = getattr(self, name, None)
            # except Exception:
            #    continue

            # if value is a parameter yield name,value
            if isinstance(value, self._Parameter):
                yield name, value


class Inputs(list):
    """
    Decorator class for list of [i,o] pairs
    """
    pass


class JSONType:
    """
    Abstract class for JSON type for parameter values.

    """
    pass
