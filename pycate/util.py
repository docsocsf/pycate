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
    s = s.lower()
    s0 = s.lower()[0]  # save calculating it all the time
    s1 = s.lower()[1]
    if s0 == "j":
        if s1 == "a":
            return 1
        elif s1 == "u":
            if s[2] == "n":
                return 6
            elif s[2] == "l":
                return 7
    elif s0 == "f":
        return 2
    elif s0 == "m":
        if s1 == "a":
            if s[2] == "r":
                return 3
            elif s[2] == "y":
                return 5
    elif s0 == "a":
        if s1 == "p":
            return 4
        elif s1 == "u":
            return 8
    elif s0 == "s":
        return 9
    elif s0 == "o":
        return 10
    elif s0 == "n":
        return 11
    elif s0 == "d":
        return 12
    return -1
