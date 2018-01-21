"""PyCate test suite"""
import pytest


@pytest.fixture
def cate():
    from pycate import CATe
    cate = CATe('tests')
    cate.__http = None
    return cate


def test_success(cate):
    assert(cate is not None)
