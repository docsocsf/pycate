"""Provides the CATe class"""

import datetime
import logging
import re

from bs4 import BeautifulSoup

from pycate.const import __version__, CATE_BASE_URL, USER_AGENT_FORMAT
from pycate.http import Http
from pycate.urls import URLs
from pycate.util import get_current_academic_year, month_search


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
            user_info_table = soup.form.table.tbody.tr.find_all('td')[1].table \
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
            timetable_selection_table = soup.form.table.tbody.contents[2].tr \
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

    def __get_default_period_and_class(self, period, clazz):
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

        return period, clazz

    def __get_timetable_table_rows(self, period=None, clazz=None):
        response = self.__get(URLs.timetable(
            get_current_academic_year()[0], period, clazz, self._username))
        soup = BeautifulSoup(response.text, 'html5lib')

        self.logger.debug('Timetable data received, parsing...')

        return soup.body.contents[3].tbody.find_all('tr')

    def get_modules(self, period=None, clazz=None, get_module_rows=False,
                    timetable_table_rows=None):
        """
        Gets a list of modules for the given period/class with their notes keys
        :param period: The period of the year to get exercises to, by default
            uses the current one
        :param clazz: The class of which the timetable should be returned, by
            default uses the user's current class.
        :param get_module_rows: If True returns information about the rows
            occupied by each module
        :param timetable_table_rows: If not None the function uses this as the
            source of timetable information
        :return:
        """

        period, clazz = self.__get_default_period_and_class(period, clazz)

        if timetable_table_rows is None:
            period, clazz = self.__get_default_period_and_class(period, clazz)
            timetable_table_rows = self.__get_timetable_table_rows(period,
                                                                   clazz)

        # Find rows containing modules
        self.logger.debug('Finding modules...')
        module_rows = list()

        for i, row in enumerate(timetable_table_rows[7:]):
            row_tds = row.find_all('td')
            if len(row_tds) >= 2:
                # Check if row contains a module by looking for the blue border
                # around the module name cell
                if ('style' in row_tds[1].attrs) and \
                        row_tds[1]['style'] == 'border: 2px solid blue':
                    module_td = row_tds[1]

                    # Find module notes
                    module_notes_key = ''
                    if module_td.a is not None:
                        module_notes_key = module_td.a['href'].split('=')[-1]

                    module_info = {
                        'name': row_tds[1].text.strip(),
                    }

                    if module_notes_key:
                        module_info['notes_key'] = module_notes_key

                    if get_module_rows:
                        module_info['start_row'] = 7 + i
                        module_info['rowspan'] = int(row_tds[1]['rowspan'])

                    module_rows.append(module_info)

        return module_rows

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

        period, clazz = self.__get_default_period_and_class(period, clazz)

        self.logger.debug('Downloading exercise timetable for {} '
                          '(year: {}, period: {}, class: {})'
                          .format(self._username,
                                  get_current_academic_year()[0],
                                  period, clazz))

        timetable_table_rows = self.__get_timetable_table_rows(period, clazz)

        # Begin calculating the first date in period
        month_row = timetable_table_rows[0]
        day_row = timetable_table_rows[2]

        month_colspans = list()
        for month in month_row.find_all('th')[1:]:
            month_colspans.append({
                'name': month.text.strip(),
                'colspan': int(month['colspan'])
            })

        # This will be a datetime representing the first date in the selected
        # period
        start_datetime = None

        for i, day in enumerate(day_row.find_all('th')[1:]):
            day = day.text.strip()
            if day != '':
                first_labelled_day = int(day)

                # Find month at first labelled day
                first_labelled_datetime = None
                k = first_labelled_day
                for month in month_colspans:
                    k -= month['colspan']

                    # If the current month hasn't been found yet keep going
                    if k > 0:
                        continue

                    first_labelled_month = month_search(month['name'])

                    # Use 1st September as the cut off between academic years
                    current_year_pair = get_current_academic_year()
                    if first_labelled_month < 9:
                        first_labelled_year = current_year_pair[1]
                    else:
                        first_labelled_year = current_year_pair[0]

                    first_labelled_datetime = datetime.datetime(
                        day=first_labelled_day,
                        month=first_labelled_month,
                        year=first_labelled_year)

                    break

                start_datetime = first_labelled_datetime - datetime.timedelta(
                    days=i)

                self.logger.debug('First labelled date is {}'.format(
                    first_labelled_datetime.strftime('%Y-%m-%d')))

                break

        self.logger.debug('Period {} begins on {}'.format(
            period, start_datetime.strftime('%Y-%m-%d')))

        # Using start_datetime as a reference, use this to work out the start
        # and end times for each exercise

        module_rows = self.get_modules(period, clazz, get_module_rows=True, timetable_table_rows=timetable_table_rows)

        # Create a list of exercises to be returned
        exercises = list()

        for module in module_rows:
            start_row = module['start_row']
            end_row = start_row + module['rowspan']

            # Construct object for module information. Number and name are (for
            # example) '113' and 'Architecture' respectively.
            module_info = {
                'number': module['name'].split(' ')[0],
                'name': ' '.join(module['name'].split(' ')[2:]),
                'notes_key': module['notes_key'],
            }

            for row_index, row in enumerate(
                    timetable_table_rows[start_row:end_row]):
                running_day_offset = 0

                # First row contains the module name element with rowspan so
                # the exercises start at a later column but the other rows just
                # contain the exercises
                if row_index == 0:
                    start_cell = 4
                else:
                    start_cell = 1

                for td in row.find_all('td')[start_cell:]:
                    # Find the number of columns the cell spans (i.e. the length
                    # of the exercise)
                    td_colspan = 1
                    if 'colspan' in td.attrs:
                        td_colspan = int(td['colspan'])

                    current_day_offset = running_day_offset
                    running_day_offset += td_colspan

                    # Remove large whitespace gaps from text in the cell to
                    # leave just the text
                    td_text = re.sub(r'\s{2,}', ' ', td.text.strip())

                    # If the cell contains no text it's just empty space and
                    # doesn't contain an exercise
                    if len(td_text) == 0:
                        continue

                    # Extract the code (i.e. 1:PMT) and actual exercise
                    # name
                    if td.span is not None:
                        exercise_code = td.span.text.strip()
                        exercise_name = td.span['title']
                    else:
                        exercise_code = td_text.split(' ')[0]
                        exercise_name = ' '.join(td_text.split(' ')[1:])

                    # Calculate the start and end dates
                    exercise_start = start_datetime + datetime.timedelta(
                        days=current_day_offset)
                    exercise_end = exercise_start + datetime.timedelta(
                        days=td_colspan - 1)

                    exercise_links = dict()

                    # Find exercise links
                    for td_link in td.find_all('a'):
                        if 'href' not in td_link.attrs:
                            continue

                        td_href = td_link['href']
                        if 'mailto' in td_href:
                            exercise_links['mailto'] = td_href
                            continue
                        if 'SPECS' in td_href:
                            spec_key = td_href[17:]
                            exercise_links['spec'] = URLs.show_file(spec_key)
                            continue
                        if 'handins.cgi' in td_href:
                            handin_key = td_href[16:]
                            exercise_links['handin'] = URLs.handin(handin_key)
                            continue
                        if 'given.cgi' in td_href:
                            given_key = td_href[14:]
                            exercise_links['givens'] = URLs.givens(given_key)
                            continue

                    # Find out unassessed/assessed status
                    exercise_assessed_status = 'UNKNOWN'
                    if 'bgcolor' in td.attrs:
                        td_bgcolor = td['bgcolor']
                        if td_bgcolor == 'white':
                            # Unassessed
                            exercise_assessed_status = 'UA'
                        elif td_bgcolor == '#cdcdcd':
                            # Unassessed - submission required
                            exercise_assessed_status = 'UA-SR'
                        elif td_bgcolor == '#ccffcc':
                            # Assessed - individual
                            exercise_assessed_status = 'A-I'
                        elif td_bgcolor == '#f0ccf0':
                            # Assessed - group
                            exercise_assessed_status = 'A-G'

                    # Find out submission status
                    exercise_submission_status = 'UNKNOWN'
                    if 'style' in td.attrs:
                        td_style = td['style']
                        if td_style == 'border: 2px solid red':
                            # Not submitted
                            exercise_submission_status = 'N-S'
                        elif td_style == 'border: 5px solid red':
                            # Not submitted - due soon
                            exercise_submission_status = 'N-S-DS'
                        elif td_style == 'border: 2px solid yellow':
                            # Incomplete submission
                            exercise_submission_status = 'I'
                        elif td_style == 'border: 5px solid yellow':
                            # Incomplete submission - due soon
                            exercise_submission_status = 'I-DS'
                    else:
                        exercise_submission_status = 'OK'

                    exercise_info = {
                        'module_number': module_info['number'],
                        'module_name': module_info['name'],
                        'code': exercise_code,
                        'name': exercise_name,
                        'start': exercise_start.strftime('%Y-%m-%d'),
                        'end': exercise_end.strftime('%Y-%m-%d'),
                        'assessed_status': exercise_assessed_status,
                        'submission_status': exercise_submission_status
                    }

                    if len(exercise_links) > 0:
                        exercise_info['links'] = exercise_links

                    # Save this info into the module's exercises list
                    exercises.append(exercise_info)

        self.logger.debug('Found {} modules, {} exercises'.format(
            len(module_rows), len(exercises)))

        return exercises

    def get_notes(self, notes_key):
        """
        Gets the notes associated with the given notes key
        :param notes_key: Notes key to query from
        :return: A list containing dictionaries with note info in
        """
        response = self.__get(URLs.module_notes(notes_key))
        soup = BeautifulSoup(response.text, 'html5lib')
        note_rows = soup.form.tbody.tbody.find_all('tr')[1:-1]
        notes = list()
        for row in note_rows:
            note_obj = dict()
            tds = row.find_all('td')
            note_obj['number'] = tds[0].text
            note_obj['title'] = tds[1].text
            note_obj['size'] = tds[3].text
            note_obj['loaded'] = tds[4].text
            note_obj['owner'] = tds[5].text
            note_obj['hits'] = tds[6].text

            if tds[2].text == "URL*":
                note_obj['type'] = "URL"
                if tds[1].a:
                    note_obj['url'] = tds[1].a['title']
            else:
                note_obj['type'] = tds[2].text
                if tds[1].a:
                    note_obj['filekey'] = tds[1].a['href'][17:]

            notes.append(note_obj)

        return notes

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
