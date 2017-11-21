import requests

from .const import CATE_BASE_URL
from .exceptions import AuthException


class Requestor(object):
    """
    The Requestor class is handles every HTTP request made by PyCate. It
    ensures the correct authorization and user agent headers are sent with
    every request.
    """

    def __init__(self, user_agent, username, password):
        """
        Initialise a Requestor. The username and password must be set as
        CATe does not use any cookies, instead relying on the correct
        authorization headers to be present in every request.

        :param user_agent: The user agent to use for all requests
        :param username: The username to use for all requests
        :param password: The password to use for all requests
        """
        self.user_agent = user_agent
        self.username = username
        self.password = password

        self._test_credentials()

    def _test_credentials(self):
        """
        Attempts to access cate in order to verify login details
        """

        r = self.get(CATE_BASE_URL)

        if r.status_code == 200:
            # Authorization succeeded
            return

        if r.status_code == 401:
            # Unauthorized
            raise AuthException("Username/password may be incorrect")

    def get(self, url):
        return requests.get(url, headers={
            'User-Agent': self.user_agent
        }, auth=(self.username, self.password))
