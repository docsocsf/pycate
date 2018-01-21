from datetime import datetime


def get_current_academic_year():
    """
    Calculates the current academic year, using 1st August 00:00 as the start of a new year
    """
    utctime = datetime.utcnow()
    if utctime.month < 8:
        academic_year_start = utctime.year - 1
        academic_year_end = utctime.year
    else:
        academic_year_start = utctime.year
        academic_year_end = utctime.year + 1

    return academic_year_start, academic_year_end