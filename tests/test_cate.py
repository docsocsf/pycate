import pytest


class TestCate:
    @pytest.fixture(name="cate")
    def create_dummy_cate(self):
        from pycate.cate import CATe
        cate = CATe('tests')
        cate.__http = None
        return cate

    def test_success(self, cate):
        assert cate is not None
