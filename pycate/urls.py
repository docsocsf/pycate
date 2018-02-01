"""
Contains functions to generate CATe URLs
"""
from .const import CATE_BASE_URL


class URLs:
    @classmethod
    def _makeurl(cls, path):
        return CATE_BASE_URL + path

    @classmethod
    def personal(cls, year, username):
        return URLs._makeurl('personal.cgi?keyp={year}:{uname}'
                             .format(year=year, uname=username))

    @classmethod
    def timetable(cls, year, period, clazz, username):
        return URLs._makeurl('timetable.cgi?keyt={year}:{period}:{cls}:{uname}'
                             .format(year=year, period=period, cls=clazz,
                                     uname=username))

    @classmethod
    def module_notes(cls, key):
        return URLs._makeurl('notes.cgi?key={}'.format(key))
