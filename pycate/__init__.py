"""
Py-Cate is a Python library designed to allow programmatic use of CATe, the
*Continous Assessment Tracking Engine* used by the Department of Computing at
Imperial College London.
"""

from pycate.const import __version__

import logging

logging.getLogger("pycate").addHandler(logging.NullHandler())
