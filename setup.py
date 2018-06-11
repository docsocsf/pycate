from setuptools import setup, find_packages

import re
from os import path

PACKAGE_NAME = "pycate"
HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(HERE, "README.rst"), encoding="utf-8") as f:
    README = f.read()

# Get version number from pycate/const.py, must be surrounded by "
with open(path.join(HERE, PACKAGE_NAME, "const.py"), encoding="utf-8") as fp:
    VERSION = re.search("__version__ = \"([^\"]+)\"", fp.read()).group(1)

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description="An API wrapper for CATe",
    long_description=README,
    url="https://github.com/docsocsf/py-cate",
    author="Fraser May",
    author_email="frasertmay@gmail.com",
    license="MIT",
    classifiers=[
        "Development Status :: 1 - Planning",
        "Environment :: Console" "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent" "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Topic :: Utilities",
    ],
    keywords="cate api imperial college",
    packages=find_packages(exclude=["contrib", "docs", "tests*"]),
    install_requires=["requests", "beautifulsoup4", "html5lib"],
    tests_require=["pytest"],
    python_requires="~=3.6",
)
