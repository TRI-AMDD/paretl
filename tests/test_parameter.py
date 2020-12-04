import pytest
from paretl import Parameter


@pytest.fixture(scope="module")
def p():
    return Parameter('name', default="foo")
