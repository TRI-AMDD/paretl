========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |requires|
        | |coveralls| |codecov|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|
.. |docs| image:: https://readthedocs.org/projects/paretl/badge/?style=flat
    :target: https://readthedocs.org/projects/paretl
    :alt: Documentation Status

.. |travis| image:: https://api.travis-ci.org/TRI-AMDD/paretl.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/TRI-AMDD/paretl

.. |requires| image:: https://requires.io/github/TRI-AMDD/paretl/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/TRI-AMDD/paretl/requirements/?branch=master

.. |coveralls| image:: https://coveralls.io/repos/TRI-AMDD/paretl/badge.svg?branch=master&service=github
    :alt: Coverage Status
    :target: https://coveralls.io/r/TRI-AMDD/paretl

.. |codecov| image:: https://codecov.io/gh/TRI-AMDD/paretl/branch/master/graphs/badge.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/TRI-AMDD/paretl

.. |version| image:: https://img.shields.io/pypi/v/paretl.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/paretl

.. |wheel| image:: https://img.shields.io/pypi/wheel/paretl.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/paretl

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/paretl.svg
    :alt: Supported versions
    :target: https://pypi.org/project/paretl

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/paretl.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/paretl

.. |commits-since| image:: https://img.shields.io/github/commits-since/TRI-AMDD/paretl/v0.3.0.svg
    :alt: Commits since latest release
    :target: https://github.com/TRI-AMDD/paretl/compare/v0.3.0...master



.. end-badges

Parameterized ETL

* Free software: Apache Software License 2.0

Installation
============

::

    pip install paretl

You can also install the in-development version with::

    pip install https://github.com/TRI-AMDD/paretl/archive/master.zip


Documentation
=============


https://paretl.readthedocs.io/


Development
===========

To run all the tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
