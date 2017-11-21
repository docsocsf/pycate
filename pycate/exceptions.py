"""
PyCate exception classes
"""


class PyCateException(Exception):
    """Base PyCate Exception all other exceptions extend from"""


class ClientException(PyCateException):
    """Exceptions that don't involve interaction with CATe"""


class AuthException(PyCateException):
    """
    Used when there is an authentication problem (e.g. incorrect credentials)
    """