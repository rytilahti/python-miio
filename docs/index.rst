.. python-miio documentation master file, created by
   sphinx-quickstart on Wed Oct 18 03:50:00 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. include:: ../README.rst

Installation
============

Please make sure you have libffi and openssl headers installed, you can
do this on Debian-based systems (like Rasperry Pi) with
``apt-get install libffi-dev libssl-dev``. Also do note that the
setuptools version is too old for installing some requirements, so
before trying to install this package you should update the setuptools
with ``pip3 install -U setuptools``.

The easiest way to install the package is to use pip:
``pip3 install python-miio`` . `Using
virtualenv <http://docs.python-guide.org/en/latest/dev/virtualenvs/>`__
is recommended.

In case you get an error similar like
``ImportError: No module named 'packaging'`` during the installation,
you need to upgrade pip and setuptools:

::

    $ pip3 install -U pip setuptools


.. toctree::
    :maxdepth: 2
    :caption: Contents:

    Home <self>
    discovery
    vacuum
    API <miio>