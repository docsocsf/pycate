"""
Py-Cate is a Python library designed to allow programmatic use of CATe, the
*Continous Assessment Tracking Engine* used by the Department of Computing at
Imperial College London.
"""

from .const import __version__
from .cate import CATe

import logging

logging.getLogger('pycate').addHandler(logging.NullHandler())
