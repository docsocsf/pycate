"""Provides the CATe class"""

import datetime
import logging
import re

from bs4 import BeautifulSoup

from .const import __version__, CATE_BASE_URL, USER_AGENT_FORMAT
from .http import Http
from .urls import URLs
from .util import get_current_academic_year, month_search


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

        self.logger.debug(
            'Authenticating user {user} (with password: {pw})'.format(
                user=username, pw=('*' * len(password)))
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

    def get_user_info(self, skip_personal=False, skip_defaults=False):
        """
        Gets user information (name, login, CID, status, department, category,
        email, personal tutor, default class and period) from the CATe homepage

        :param skip_personal: If True, the user info is omitted
        :param skip_defaults: If True, the default class and period are omitted
        :return:
        """
        self.logger.debug('Getting user info for {}...'.format(self._username))

        url = URLs.personal(get_current_academic_year()[0], self._username)

        response = self.__get(url)
        soup = BeautifulSoup(response.text, 'html5lib')

        user = dict()

        if not skip_personal:
            user_info_table = soup.form.table.tbody.tr.find_all('td')[1].table\
                .tbody
            uit_rows = user_info_table.find_all('tr')

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
        else:
            self.logger.debug('Skipping personal info...')

        if not skip_defaults:
            timetable_selection_table = soup.form.table.tbody.contents[2].tr\
                .find_all('table')
            period_table = timetable_selection_table[2]
            class_table = timetable_selection_table[3]

            period_inputs = period_table.find_all('input')
            clazz_inputs = class_table.find_all('input')

            period_selected = None
            class_selected = None

            for p_input in period_inputs:
                if p_input.has_attr('checked'):
                    period_selected = p_input['value']

            for c_input in clazz_inputs:
                if c_input.has_attr('checked'):
                    class_selected = c_input['value']

            user['default_period'] = period_selected
            user['default_class'] = class_selected
        else:
            self.logger.debug('Skipping default class/period')

        self.logger.debug('Got user info for {}...'.format(self._username))

        return user

    def get_exercise_timetable(self, period=None, clazz=None):
        """
        Gets the exercise timetable for the current user from the CATe exercise
        timetable
        :param period: The period of the year to get exercises to, by default
            uses the current one
        :param clazz: The class of which the timetable should be returned, by
            default uses the user's current class.
        :return:
        """
        self.logger.debug('Getting exercise timetable for {}...'
                          .format(self._username))

        # If either is None, will need to go to personal page to get defaults
        if period is None or clazz is None:
            self.logger.debug('Period/Clazz is None, finding defaults...')

            user_info = self.get_user_info(skip_personal=True)

            if period is None:
                period = user_info['default_period']
                self.logger.debug('Setting period to: {}'.format(period))

            if clazz is None:
                clazz = user_info['default_class']
                self.logger.debug('Setting class to:  {}'.format(clazz))

        self.logger.debug('Downloading exercise timetable for {} '
                          '(year: {}, period: {}, class: {})'
                          .format(self._username,
                                  get_current_academic_year()[0],
                                  period, clazz))

        timetable_response = self.__get(URLs.timetable(
            get_current_academic_year()[0], period, clazz, self._username))
        timetable_soup = BeautifulSoup(timetable_response.text, 'html5lib')

        self.logger.debug('Timetable data received, parsing...')

        timetable_table_rows = timetable_soup.body.contents[
            3].tbody.find_all('tr')

        # Begin calculating the first date in period
        month_row = timetable_table_rows[0]
        day_row = timetable_table_rows[2]

        month_colspans = list()
        for month in month_row.find_all('th')[1:]:
            month_colspans.append({
                'name': month.text.strip(),
                'colspan': int(month['colspan'])
            })

        start_datetime = None

        for i, day in enumerate(day_row.find_all('th')[1:]):
            day = day.text.strip()
            if day != '':
                first_labelled_day = int(day)
                # find month at first labelled day
                k = first_labelled_day
                first_labelled_datetime = None
                for month in month_colspans:
                    k -= month['colspan']
                    if k <= 0:
                        first_labelled_month = month['name']
                        first_labelled_month_number = month_search(
                            first_labelled_month)
                        # If first labelled month is before september, assume at
                        # the start of next year
                        current_year_pair = get_current_academic_year()
                        if first_labelled_month_number < 9:
                            first_labelled_year = current_year_pair[1]
                        else:
                            first_labelled_year = current_year_pair[0]

                        first_labelled_datetime = datetime.datetime(
                            day=first_labelled_day,
                            month=first_labelled_month_number,
                            year=first_labelled_year)

                        break

                start_datetime = first_labelled_datetime - datetime.timedelta(
                    days=i)

                self.logger.debug('First labelled date is {}'.format(
                    first_labelled_datetime.strftime('%Y-%m-%d')))

                break

        self.logger.debug('Period {} begins on {}'
                          .format(period, start_datetime.strftime('%c')))

        # Using start_datetime as a reference, use this to work out the start
        # and end times for each exercise

        # Find rows containing modules
        self.logger.debug('Finding modules...')
        modules = list()

        for i, row in enumerate(timetable_table_rows[7:]):
            row_tds = row.find_all('td')
            if len(row_tds) >= 2:
                if ('style' in row_tds[1].attrs) and \
                        row_tds[1]['style'] == 'border: 2px solid blue':
                    modules.append({
                        'name': row_tds[1].text.strip(),
                        'start_row': 7 + i,
                        'rowspan': int(row_tds[1]['rowspan'])
                    })

        self.logger.debug('Found {} modules'.format(len(modules)))

        for module in modules:
            module['exercises'] = list()
            module_name = module['name']
            current_day_offset = 0
            start_row = module['start_row']
            end_row = start_row + module['rowspan']

            print('MODULE: {}'.format(module_name))

            for row_index, row in enumerate(
                    timetable_table_rows[start_row:end_row]):
                if row_index == 0:
                    start_cell = 4
                else:
                    start_cell = 2

                for td in row.find_all('td')[start_cell:]:
                    if td.text is not None:
                        td_colspan = 1
                        if 'colspan' in td.attrs:
                            td_colspan = int(td['colspan'])

                        exercise_start = start_datetime + datetime.timedelta(
                            days=current_day_offset - 1)
                        exercise_end = exercise_start + datetime.timedelta(
                            days=td_colspan)
                        current_day_offset += td_colspan
                        td_text_without_whitespace = re.sub(r'\s{2,}', ' ',
                                                            td.text.strip())

                        if len(td_text_without_whitespace) > 0:
                            print(' >  {} ({} - {})'.format(
                                td_text_without_whitespace,
                                exercise_start.strftime('%Y-%m-%d'),
                                exercise_end.strftime('%Y-%m-%d')
                            ))

                            module['exercises'].append({
                                'name': td_text_without_whitespace,
                                'start': exercise_start.strftime('%Y-%m-%d'),
                                'end': exercise_end.strftime('%Y-%m-%d')
                            })

            print('-' * 100)

        return start_datetime

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
