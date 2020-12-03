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
.. |docs| image:: https://readthedocs.org/projects/petl/badge/?style=flat
    :target: https://readthedocs.org/projects/petl
    :alt: Documentation Status

.. |travis| image:: https://api.travis-ci.org/TRI-AMDD/petl.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/TRI-AMDD/petl

.. |requires| image:: https://requires.io/github/TRI-AMDD/petl/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/TRI-AMDD/petl/requirements/?branch=master

.. |coveralls| image:: https://coveralls.io/repos/TRI-AMDD/petl/badge.svg?branch=master&service=github
    :alt: Coverage Status
    :target: https://coveralls.io/r/TRI-AMDD/petl

.. |codecov| image:: https://codecov.io/gh/TRI-AMDD/petl/branch/master/graphs/badge.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/TRI-AMDD/petl

.. |version| image:: https://img.shields.io/pypi/v/petl.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/petl

.. |wheel| image:: https://img.shields.io/pypi/wheel/petl.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/petl

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/petl.svg
    :alt: Supported versions
    :target: https://pypi.org/project/petl

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/petl.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/petl

.. |commits-since| image:: https://img.shields.io/github/commits-since/TRI-AMDD/petl/v0.1.0.svg
    :alt: Commits since latest release
    :target: https://github.com/TRI-AMDD/petl/compare/v0.1.0...master



.. end-badges

Parameterized ETL

* Free software: Apache Software License 2.0

Installation
============

::

    pip install petl

You can also install the in-development version with::

    pip install https://github.com/TRI-AMDD/petl/archive/master.zip


Documentation
=============


https://petl.readthedocs.io/


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
