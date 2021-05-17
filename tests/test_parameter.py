import pytest
from paretl import ParameterizingOut, Parameter, JSONType


@pytest.fixture()
def par():
    return Parameter('name', default="foo")


@pytest.fixture()
def cls(par):
    def f(p):
        f.parameter1 = p
        f._private = 0
        f.not_a_parameter = 0
    f(par)
    return f


@pytest.fixture()
def o(cls):
    out = ParameterizingOut(cls, Parameter, JSONType)
    return out


@pytest.fixture()
def args():
    return ['flow.py', 'run', '--parameter1', 'bar', '--tag', 'ignore']


@pytest.fixture()
def help_args():
    return ['--help', 'flow.py', 'run', '--parameter1', 'bar', '--tag', 'ignore']


def test_can_read_parameter_defaults(o):
    o.read_parameter_defaults()
    assert o.parameter1 == 'foo'
    assert not hasattr(o, 'not_a_parameter')
    assert not hasattr(o, '_private')


def test_can_read_parameter_overrides(o, args):
    o.read_parameter_defaults()
    o.read_parameter_overrides(args)
    assert o.parameter1 == 'bar'
    assert not hasattr(o, 'tag')


def test_can_help(o, help_args):
    o.read_parameter_defaults()
    o.read_parameter_overrides(help_args)
    assert o.parameter1 == 'bar'
    assert not hasattr(o, 'tag')


def test_can_inject_parameter_type(par):
    class Foo(Parameter):
        pass
    impl = par.as_injected(Foo)
    assert type(impl) == Foo
    assert impl.name == par.name
    assert impl.default == par.default
