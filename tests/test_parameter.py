import pytest
import json
from paretl import ParameterizingOut, Parameter, JSONType, Parameterized, ETL, In, Out, timeit, tim, Sweep


@pytest.fixture()
def par():
    return Parameter('name', default="foo")


@pytest.fixture()
def par2():
    return Parameter('size', default="bar", custom=[20])


@pytest.fixture()
def args():
    return ['flow.py', 'run', '--parameter1', 'bar', '--tag', 'ignore']


@pytest.fixture()
def help_args():
    return ['--help', 'flow.py', 'run', '--parameter1', 'bar', '--tag', 'ignore']


@pytest.fixture()
def resume_args():
    return ['flow.py', 'resume', '--tag', 'parameter1:foo', '--tag', 'parameter2:bar']


@pytest.fixture()
def sweep_json():
    return '{"parameter1":[1,2,3],"parameter2":[10,20]}'


@pytest.fixture()
def sweep_json2():
    return '{"parameter1":[-1,-2,-3],"parameter2":[-10,-20]}'


@pytest.fixture()
def sweep_args(sweep_json2):
    return ['flow.py', 'run', '--sweep', sweep_json2, '--tag', 'ignore']


@pytest.fixture()
def par_sweep(sweep_json):
    return Parameter('sweep', default=sweep_json, type=JSONType)


@pytest.fixture()
def cls(par, par_sweep):
    def f(p):
        f.parameter1 = p
        f.sweep = par_sweep
        f._private = 0
        f.not_a_parameter = 0
    f(par)
    return f


@pytest.fixture()
def o(cls):
    out = ParameterizingOut(cls, Parameter, JSONType)
    return out


@pytest.fixture()
def i():
    return In()


@pytest.fixture()
def io():
    return [[In(), Out()]]


@pytest.fixture()
def get_etl(par, par2):
    class Model(ETL):
        etl_parameter = par
        parameter1 = par
        parameter2 = par2
        parameter3 = Parameter('par3', default=42)

        @tim
        def task(self, log_time={}):
            return 42

        def do_sweep(self, i, o):
            ls = list(o.sweep.items())
            sweep1var, sweep1val = ls[o.sweep_index]
            o.sweep_index += 1

            setattr(o, sweep1var, sweep1val[0])

            sweep1 = Sweep(sweep1var, i, o)
            for a in sweep1val:
                i, o = sweep1.add(a)
                o.a = o.parameter1
                o.b = o.etl_parameter
                o.c = o.parameter3
            i, o = sweep1.load()
            sweep1.load_io()

        def load(self, i, o):
            if hasattr(o, 'sweep'):
                self.do_sweep(i, o)
            o.result = self.task()
            o.result = self.task(log_time={})
            super().load(i, o)
    return lambda i, o: Model(i, o)


@pytest.fixture()
def parameterized(get_etl, par):
    class Script(Parameterized):
        factories = {"get_etl": get_etl}
        doc = "A parameterized script"
        _Parameter = Parameter
        _JSONType = JSONType
        parameter1 = par

        def populate(self):
            # get default parameter values from parameterized class
            for var in dir(self):
                if var[0] == '_':
                    continue
                val = getattr(self, var)
                if isinstance(val, self._Parameter):
                    default = val.kwargs['default']
                    setattr(self, var, json.loads(default) if val.type == self._JSONType else default)

    return Script


@pytest.fixture()
def sweeping(parameterized, par_sweep):
    class Sweeping(parameterized):
        sweep = par_sweep

    return Sweeping


def test_can_read_parameter_defaults(o):
    o.read_parameter_defaults()
    assert o.parameter1 == 'foo'
    assert not hasattr(o, 'not_a_parameter')
    assert not hasattr(o, '_private')


def test_can_read_parameter_overrides(o, args):
    o.read_parameter_defaults()
    o.read_parameter_overrides([])
    o.read_parameter_overrides(args)
    assert o.parameter1 == 'bar'
    assert not hasattr(o, 'tag')


def test_can_parse_parameter_sweep(o, sweep_json):
    o.parse_sweep(sweep_json)
    assert o.parameter1 == 1
    assert o.parameter2 == 10
    assert o.parameterized.parameter1 == 'swept'
    assert o.sweep['parameter1'] == [1, 2, 3]
    assert o.sweep['parameter2'] == [10, 20]


def test_can_read_parameter_values(o, args):
    o.read_parameter_values()
    assert o.parameter1 == 1
    assert o.parameter2 == 10
    assert o.parameterized.parameter1 == 'swept'


def test_can_read_sweep_override(o, sweep_args):
    o.read_parameter_values(sweep_args)
    assert o.parameter1 == -1
    assert o.parameter2 == -10
    assert o.parameterized.parameter1 == 'swept'
    assert o.sweep['parameter1'] == [-1, -2, -3]


def test_can_parameterize_help(o, help_args):
    o.read_parameter_defaults()
    o.read_parameter_overrides(help_args)
    assert o.parameter1 == 'bar'
    assert not hasattr(o, 'tag')


def test_can_parameterize_resume(o, resume_args):
    o.read_parameter_defaults()
    o.read_parameter_overrides(resume_args)
    assert o.parameter1 == 'foo'
    assert not hasattr(o, 'tag')


def test_can_inject_parameter_type(par):
    class Foo(Parameter):
        pass
    impl = par.as_injected(Foo)
    assert type(impl) == Foo
    assert impl.name == par.name
    assert impl.default == par.default


def test_can_add_parameter(o, par, par_sweep):
    o.add_parameter('par1', par)
    o.add_parameter('par1', par)
    o.add_parameter('sweep', par_sweep)
    o.add_parameter('sweep', par_sweep)
    assert o.par1 == par.default
    assert o.sweep['parameter1'] == [1, 2, 3]
    assert o.parameterized.par1.default == par.default
    assert o.parameterized.sweep.default == par_sweep.default


def test_can_parameterize(parameterized):
    script = parameterized()
    assert script.parameter1.default == "foo"
    assert script.etl_parameter.default == "foo"


def test_can_parameterize_sweep(sweeping, sweep_json):
    script = sweeping()
    assert script.parameter1 == "swept"
    assert script.sweep.default == sweep_json


def test_can_autotag(parameterized, args):
    script = parameterized()
    script.add_parameter_tags(args=args)
    assert args[-8:] == ['--tag', 'parameter1:bar', '--tag', 'etl_parameter:foo', '--tag', 'parameter2:bar', '--tag', 'parameter3:42']


def test_can_process_input(sweeping, i):
    script = sweeping()
    script.timeit = timeit
    script.populate()
    script.process(i)
    script.etl.et(i, script)
    script.etl.tl(i, script)
    assert script.result == 42


def test_can_process_list(parameterized, io):
    script = parameterized()
    script.process(io)
    assert script.result == 42
