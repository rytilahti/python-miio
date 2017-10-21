Getting started
***************

Installation
============

The easiest way to install the package is to use pip:
``pip3 install python-miio`` . `Using
virtualenv <http://docs.python-guide.org/en/latest/dev/virtualenvs/>`__
is recommended.


Please make sure you have ``libffi`` and ``openssl`` headers installed, you can
do this on Debian-based systems (like Rasperry Pi) with

.. code-block:: bash

    apt-get install libffi-dev libssl-dev

Depending on your installation, the setuptools version may be too old
for some dependencies so before reporting an issue please try to update
the setuptools package with

.. code-block:: bash

    pip3 install -U setuptools

In case you get an error similar like
``ImportError: No module named 'packaging'`` during the installation,
you need to upgrade pip and setuptools:

.. code-block:: bash

    pip3 install -U pip setuptools

Device discovery
================
Devices already connected on the same network where the command-line tool is run
are automatically detected when ``mirobo discover`` is invoked.

To be able to communicate with devices their IP address and a device-specific encryption token must be known.
If the discovery returned a token with characters other than ``0``\ s or ``f``\ s,
that is likely a valid token for the given device and can be used directly.
In case that is not the case, the token needs to be found out other ways, e.g. by :ref:`extracting from backups <creating_backup>`
of the Mi Home application.

.. IMPORTANT::

    For some devices (e.g. the vacuum cleaner) the automatic discovery works only before the device has been connected over the app to your local wifi.
    This does not work starting from firmware version 3.3.9\_003077 onwards, in which case the procedure shown in :ref:`creating_backup` has to be used
    to obtain the token.

.. NOTE::

    Some devices also do not announce themselves via mDNS (e.g. Philips' bulbs,
    and the vacuum when not connected to the Internet),
    but are nevertheless discoverable by using a miIO discovery.
    See :ref:`handshake_discovery` for more information about the topic.

.. _handshake_discovery:

Discovery by a handshake
------------------------

The devices supporting miIO protocol answer to a broadcasted handshake packet,
which also sometime contain the required token.

Executing ``mirobo discover`` with ``--handshake 1`` option will send the handshake packet,
which may yield an usable token.

.. code-block:: bash

    $ mirobo discover --handshake 1
    INFO:miio.device:  IP 192.168.8.1: Xiaomi Mi Robot Vacuum - token: b'ffffffffffffffffffffffffffffffff'


.. NOTE::
    This method can also be useful for devices not yet connected to any network.
    In those cases the device trying to do the discovery has to connect to the
    network advertised by the corresponding device (e.g. rockrobo-XXXX for vacuum)


Tokens full of ``0``\ s or ``f``\ s (as above) are either already paired
with the mobile app or will not yield a token through this method.
In those cases the procedure shown next in :ref`creating_backup` has to be used.

.. _creating_backup:

Tokens from backups
===================

If you are reading this, the automatic extraction of tokens did not apparently work.
There is another way to get the tokens which works by extracting them from a database of the Mi Home app.
For this to work the devices have to be added to the mobile app before the database (or backup) is extracted.

Creating a backup
-----------------

The first step to do this is to extract either a database file or a backup from the Mi Home app.
A procedure to do that will be described next.

You may also find instructions in the following links useful:

- https://github.com/jghaanstra/com.xiaomi-miio/blob/master/docs/obtain\_token\_mirobot\_new.md
- https://github.com/homeassistantchina/custom_components/blob/master/doc/chuang_mi_ir_remote.md

Android
~~~~~~~

To do a backup of an Android app you need to have the developer mode active.

.. TODO::
    Add a link how to enable the developer mode.
    This part of documentation needs your help!
    Please consider submitting a pull request to update this.

After you have connected your device to your computer,
and installed the Android developer tools,
you can use ``adb`` tool to create a backup.

.. code-block:: bash

    adb backup -noapk com.xiaomi.smarthome -f backup.ab

.. NOTE::
    Depending on your Android you may need to insert a password
    and/or accept the backup, so check your phone at this point!

If everything went fine and you got a ``backup.ab`` file please continue to :ref:`token_extraction`.

Apple
~~~~~

.. TODO::
    This part of documentation needs your help!
    Please consider submitting a pull request to update this.

asdfdsf

.. _token_extraction:


Extracting tokens
-----------------

Now having extract either a backup or a database from the application,
the ``miio-extract-tokens`` can be used to extract the tokens from it.

At the moment extracting tokens from a backup (Android) or from an extracted database (Android, Apple) are supported.

Encrypted tokens as recently introduced on iOS devices will be automatically decrypted.
For decrypting encrypted Android backups the password has to be given to the command with ``--password <password>``.

*Please feel free to submit pull requests to simplify this procedure!*

.. code-block:: bash

    $ miio-extract-tokens backup.ab
    Opened backup/backup.ab
    Extracting to /tmp/tmpvbregact
    Reading tokens from Android DB
    Gateway
            Model: lumi.gateway.v3
            IP address: 192.168.XXX.XXX
            Token: 91c52a27eff00b954XXX
            MAC: 28:6C:07:XX:XX:XX
    room1
            Model: yeelink.light.color1
            IP address: 192.168.XXX.XXX
            Token: 4679442a069f09883XXX
            MAC: F0:B4:29:XX:XX:XX
    room2
            Model: yeelink.light.color1
            IP address: 192.168.XXX.XXX
            Token: 7433ab14222af5792XXX
            MAC: 28:6C:07:XX:XX:XX
    Flower Care
            Model: hhcc.plantmonitor.v1
            IP address: 134.XXX.XXX.XXX
            Token: 124f90d87b4b90673XXX
            MAC: C4:7C:8D:XX:XX:XX
    Mi Robot Vacuum
            Model: rockrobo.vacuum.v1
            IP address: 192.168.XXX.XXX
            Token: 476e6b70343055483XXX
            MAC: 28:6C:07:XX:XX:XX


Environment variables for command-line tools
============================================

To simplify the use, instead of passing the IP and the token as a
parameter for the tool, you can simply set the following environment variables.
The following works for `mirobo`, see the documentation of other tools
in their documentation.

.. code-block:: bash

    export MIROBO_IP=192.168.1.2
    export MIROBO_TOKEN=476e6b70343055483230644c53707a12
