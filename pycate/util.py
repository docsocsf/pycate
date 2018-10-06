from datetime import datetime


def get_current_academic_year():
    """
    Calculates the current academic year, using 1st August 00:00 as the start of
    a new year
    """
    utctime = datetime.utcnow()
    if utctime.month < 8:
        academic_year_start = utctime.year - 1
        academic_year_end = utctime.year
    else:
        academic_year_start = utctime.year
        academic_year_end = utctime.year + 1

    return academic_year_start, academic_year_end


def month_search(s):
    """
    Tries to match the given month name with a month number (1-12)
    """
    m = {
        'jan': 1,
        'feb': 2,
        'mar': 3,
        'apr': 4,
        'may': 5,
        'jun': 6,
        'jul': 7,
        'aug': 8,
        'sep': 9,
        'oct': 10,
        'nov': 11,
        'dec': 12
    }
    s = s.strip()[:3].lower()
    if s in m:
        return m[s]
    return -1
