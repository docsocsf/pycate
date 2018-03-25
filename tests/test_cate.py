import pytest

from pycate.http import Http
from pycate.urls import URLs
from pycate.util import get_current_academic_year


class TestCate:
    @pytest.fixture(name="cate")
    def create_dummy_cate(self):
        from pycate.cate import CATe
        cate = CATe('tests', http=DummyHttp('tests'))
        return cate

    def test_userinfo(self, cate):
        info = cate.get_user_info()

        assert info.name == 'CATE_TEST_NAME'
        assert info.login == 'CATE_TEST_LOGIN'
        assert info.cid == 'CATE_TEST_CID'
        assert info.status == 'CATE_TEST_STATUS'
        assert info.department == 'CATE_TEST_DEPT'
        assert info.category == 'CATE_TEST_CATEGORY'
        assert info.email == 'CATE_TEST_EMAIL'
        assert info.personal_tutor == 'CATE_TEST_PT_NAME ' \
                                      '(CATE_TEST_PT_LOGIN)'


class DummyResponse:
    def __init__(self, text):
        self.text = text


class DummyHttp(Http):
    def get(self, url, username, password):
        if url == URLs.personal(get_current_academic_year()[0], ''):
            with open('tests/pages/personal.html') as f:
                return DummyResponse(f.read())
