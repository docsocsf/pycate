"""
Contains functions to generate CATe URLs
"""


class URLs:
    @classmethod
    def personal(cls, year, username):
        return 'https://cate.doc.ic.ac.uk/personal.cgi?keyp={year}:' \
               '{uname}'.format(year=year, uname=username)

    @classmethod
    def timetable(cls, year, period, clazz, username):
        return 'https://cate.doc.ic.ac.uk/timetable.cgi?keyt={year}:{period}:' \
               '{cls}:{uname}'.format(year=year, period=period, cls=clazz,
                                      uname=username)
