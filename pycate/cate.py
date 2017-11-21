"""Provides the CATe class"""

import logging

import requests

from .const import __version__, USER_AGENT_FORMAT
from .exceptions import ClientException
from .http import HTTP


class CATe(object):
    """
    The CATe class provides access to the data on CATe.

    Instances of this class are the way to interact with CATe. The way to
    obtain an instance of this class is:

    .. code-block:: python

       import pycate

       cate = pycate.CATe('<username> doing some testing')

    """

    def __init__(self, user_agent, username, password):
        """
        Initialize a CATe Instance. CATe does not use session cookies, instead
        relying on every request to send an Authorization header so a
        username and password is needed.

        :param user_agent: A helpful string to identify your application in
            its requests to CATe. Common strings include the name off the
            application and some way to identify you (e.g. DoC username)
        :param username: Username of the account to use
        :param password: Password of the account to use
        """

        # Create http client
        self.http = HTTP(
            USER_AGENT_FORMAT.format(user_agent),
            username,
            password
        )

        logging.getLogger('pycate').debug(
            "Initialising PyCate v{v} with user agent `{ua}`".format(
                v=__version__,
                ua=self.http.user_agent
            ))
