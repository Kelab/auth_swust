from os import getenv as _
import sys

import pytest
from auth_swust import Login
from loguru import logger

logger.remove()
logger.add(sys.stdout, level="DEBUG")


class TestLogin:
    def test_auth_fail(self):
        login = Login("5120170000", "000000")
        res, info = login.try_login()
        print(res)
        assert res is False
        print(info)
        assert info == "AuthFail"

    def test_auth_success(self):
        u = _("testusername")
        p = _("testpassword")
        if not (u and p):
            pytest.skip(msg="requires testusername and testpassword to test success")
        login = Login(u, p)
        res, info = login.try_login()
        print(res)
        assert res is True
