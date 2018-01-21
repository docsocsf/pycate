"""Provides the CATe class"""

import logging

from bs4 import BeautifulSoup

from .const import __version__, CATE_BASE_URL, USER_AGENT_FORMAT
from .http import Http
from .util import get_current_academic_year


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
        self._is_authenticated = False
        self._username = ""
        self._password = ""
        self.logger = logging.getLogger('pycate')

        self.logger.debug(
            "Initialised PyCate v{v} with user agent `{ua}`".format(
                v=__version__,
                ua=self.__http.user_agent
            ))

    def is_authenticated(self):
        """
        :return: Whether or not the CATe instance is authenticated
        """
        return self._is_authenticated

    def authenticate(self, username, password):
        """
        Authenticates a user against CATe. If authentication succeeds the
        credentials are saved in the CATe instance for future uses.

        :param username: The username to authenticate with
        :param password: The password to authenticate with
        :return: True if authentication was successful, False otherwise
        """

        def asterisk_password(pw):
            return '{}{}{}'.format(pw[0], '*' * (len(pw) - 2), pw[-1])

        self.logger.debug(
            'Authenticating user {user} (with password: {pw})'
            .format(user=username, pw=asterisk_password(password))
        )

        r = self.__get(CATE_BASE_URL, username=username, password=password)

        if r.status_code == 200:
            # Authorization succeeded
            self.logger.debug('Authentication succeeded')
            self._is_authenticated = True
            self._username = username
            self._password = password
            return True

        if r.status_code == 401:
            # Unauthorized
            self.logger.warning('Authentication failed')
            self._is_authenticated = False
            self._username = ''
            self._password = ''
            return False

    def get_user_info(self):
        """
        Gets user information (name, login, CID, status, department, category,
        email, and personal tutor) from the CATe homepage

        :return:
        """
        self.logger.debug('Getting user info for {}...'.format(self._username))

        url = 'https://cate.doc.ic.ac.uk/personal.cgi?keyp={}:{}'.format(
            get_current_academic_year()[0],
            self._username
        )

        response = self.__get(url)
        soup = BeautifulSoup(response.text, 'html5lib')

        user_info_table = soup.form.table.tbody.tr.find_all('td')[1].table.tbody
        uit_rows = user_info_table.find_all('tr')

        user = dict()

        user['name'] = uit_rows[0].find_all('td')[1].text
        user['login'] = uit_rows[1].find_all('td')[0].b.text
        user['cid'] = uit_rows[1].find_all('td')[2].b.text
        user['status'] = uit_rows[2].find_all('td')[0].b.text
        user['department'] = uit_rows[2].find_all('td')[2].b.text
        user['category'] = uit_rows[3].find_all('td')[0].b.text
        user['email'] = uit_rows[4].find_all('td')[0].b.text
        user['personal_tutor'] = '{x[0]} {x[2]}'.format(
            x=uit_rows[5].find_all('td')[0].b.contents
        )

        self.logger.debug('Got user info for {}...'.format(self._username))

        return user

    def __get(self, url, username=None, password=None):
        """
        Internal method which checks if the CATe instance has an Http instance
        then calls the get method
        :param url: The URL to perform a GET request to
        :return: The results of the GET request or None if no instance
        """
        if self.__http:
            if not username and not password:
                return self.__http.get(url, self._username, self._password)
            else:
                return self.__http.get(url, username, password)
        else:
            return None
