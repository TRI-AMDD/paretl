import pytest
from paretl import DebugIn, DebugOut


@pytest.fixture()
def i():
    return DebugIn()


@pytest.fixture()
def o():
    return DebugOut()


@pytest.fixture()
def parameter():
    def f(x):
        f.default = x
    f('foo')
    return f


@pytest.fixture()
def logger():
    def f(k, v):
        setattr(f, k, v)
    return f


def test_can_debug_input(i):
    i.foo = 'bar'
    assert i.foo == 'bar'


def test_can_debug_output(o, parameter):
    o.add_parameter('par', parameter)
    # should ignore second call with same parameter name
    o.add_parameter('par', None)
    o.foo = 'bar'
    assert o.foo == 'bar'


def test_can_log_output(logger):
    o = DebugOut(logger=logger)
    o.foo = 'bar'
    assert o.foo == 'bar'
    assert logger.foo == 'bar'


def test_can_hide_output(logger):
    o = DebugOut(logger=logger, hide=['foo'])
    o.foo = 'bar'
    assert o.foo == 'bar'
    assert not hasattr(logger, 'foo')
