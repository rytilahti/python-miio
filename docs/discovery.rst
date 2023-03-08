Getting started
***************

.. contents:: Contents
   :local:

Installation
============

You can install the most recent release using pip:

.. code-block:: console

    pip install python-miio


Alternatively, you can clone this repository and use poetry to install the current master:

.. code-block:: console

    git clone https://github.com/rytilahti/python-miio.git
    cd python-miio/
    poetry install

This will install python-miio into a separate virtual environment outside of your regular python installation.
You can then execute installed programs (like ``miiocli``):

.. code-block:: console

    poetry run miiocli --help

.. tip::

    If you want to execute more commands in a row, you can activate the
    created virtual environment to avoid typing ``poetry run`` for each
    invocation:

    .. code-block:: console

        poetry shell
        miiocli --help
        miiocli discover


Device discovery
================

Devices already connected to the same network where the command-line tool
is run are automatically detected when ``miiocli discover`` is invoked.
This command will execute two types of discovery: discovery by handshake and discovery by mDNS.
mDNS discovery returns information that can be used to detect the device type which does not work with all devices.
The handshake method works on all MiIO devices and may expose the token needed to communicate
with the device, but does not provide device type information.

To be able to communicate with devices their IP address and a device-specific
encryption token must be known.
If the returned a token is with characters other than ``0``\ s or ``f``\ s,
it is likely a valid token which can be used directly for communication.


.. _obtaining_tokens:

Obtaining tokens
================

The ``miiocli`` tool can fetch the tokens from the cloud if you have `micloud <https://github.com/squachen/micloud>`_ package installed.
Executing the command will prompt for the username and password,
as well as the server locale to use for fetching the tokens.

.. code-block:: console

    miiocli cloud list

    Username: example@example.com
    Password:
    Locale (all, cn, de, i2, ru, sg, us): all


Alternatively, you can try one of the :ref:`legacy ways to obtain the tokens<legacy_token_extraction>`.

You can also access this functionality programatically using :class:`miio.cloud.CloudInterface`.


Environment variables for command-line tools
============================================

To simplify the use, instead of passing the IP and the token as a
parameter for the tool, you can simply set the following environment variables.
The following works for `mirobo`, for other tools you should consult
the documentation of corresponding tool.

.. code-block:: bash

    export MIROBO_IP=192.168.1.2
    export MIROBO_TOKEN=476e6b70343055483230644c53707a12
