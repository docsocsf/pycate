"""Provides the CATe class"""

import logging

from .const import __version__, CATE_BASE_URL, USER_AGENT_FORMAT
from .exceptions import AuthException
from .http import Http


class CATe(object):
    """
    The CATe class provides access to the data on CATe.

    Instances of this class are the way to interact with CATe. The way to
    obtain an instance of this class is:

    .. code-block:: python

       import pycate

       cate = pycate.CATe('<username> doing some testing')
    """

    def __init__(self, user_agent):
        """
        Initialize a CATe Instance

        :param user_agent: A helpful string to identify your application in
            its requests to CATe. Common strings include the name of the
            application and some way to identify you (e.g. DoC username)
        """

        self.__http = Http(USER_AGENT_FORMAT.format(user_agent))
        self.username = ""
        self.password = ""
        self.logger = logging.getLogger('pycate')

        self.logger.debug(
            "Initialised PyCate v{v} with user agent `{ua}`".format(
                v=__version__,
                ua=self.__http.user_agent
            ))

    def authenticate(self, username, password):
        """
        Authenticates a user against CATe. If authentication succeeds the
        credentials are saved in the CATe instance for future uses.

        :param username: The username to authenticate with
        :param password: The password to authenticate with
        """
        self.logger.debug('Authenticating...')

        r = self.__get(CATE_BASE_URL, username=username, password=password)

        if r.status_code == 200:
            # Authorization succeeded
            self.username = username
            self.password = password

        if r.status_code == 401:
            # Unauthorized
            raise AuthException("Username/password may be incorrect")

    def __get(self, url, username=None, password=None):
        """
        Internal method which checks if the CATe instance has an Http instance
        then calls the get method
        :param url: The URL to perform a GET request to
        :return: The results of the GET request or None if no instance
        """
        if self.__http:
            if not username and not password:
                return self.__http.get(url, self.username, self.password)
            else:
                return self.__http.get(url, username, password)
        else:
            return None
