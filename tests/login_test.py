import unittest

from auth_swust import Login


class LoginTestEvent(unittest.TestCase):
    def test_auth_fail(self):
        login = Login("5120170000", "000000")
        res, info = login.try_login()

        assert res is False
        assert info == "AuthFail"
