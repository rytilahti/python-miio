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
Devices already connected on the same network where the command-line tool
is run are automatically detected when ``mirobo discover`` is invoked.

To be able to communicate with devices their IP address and a device-specific
encryption token must be known.
If the returned a token is with characters other than ``0``\ s or ``f``\ s,
it is likely a valid token which can be used directly for communication.
If not, the token needs to be extracted from the Mi Home Application,
see :ref:`logged_tokens` for information how to do this.

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

Executing ``mirobo discover`` with ``--handshake 1`` option will send
a broadcast handshake.
Devices supporting the protocol will response with a message
potentially containing a valid token.

.. code-block:: bash

    $ mirobo discover --handshake 1
    INFO:miio.device:  IP 192.168.8.1: Xiaomi Mi Robot Vacuum - token: b'ffffffffffffffffffffffffffffffff'


.. NOTE::
    This method can also be useful for devices not yet connected to any network.
    In those cases the device trying to do the discovery has to connect to the
    network advertised by the corresponding device (e.g. rockrobo-XXXX for vacuum)


Tokens full of ``0``\ s or ``f``\ s (as above) are either already paired
with the mobile app or will not yield a token through this method.
In those cases the procedure shown in :ref:`logged_tokens` has to be used.

.. _logged_tokens:

Tokens from Mi Home logs
========================

The easiest way to obtain tokens is to browse through log files of the Mi Home
app version 5.4.49 for Android. It seems that version was released with debug
messages turned on by mistake. An APK file with the old version can be easily
found using one of the popular web search engines. After downgrading use a file
browser to navigate to directory ``SmartHome/logs/plug_DeviceManager``, then
open the most recent file and search for the token. When finished, use Google
Play to get the most recent version back.

.. _creating_backup:

Tokens from backups
===================

Extracting tokens from a Mi Home backup is the preferred way to obtain tokens
if they cannot be looked up in the Mi Home app version 5.4.49 log files
(e.g. no Android device around).
For this to work the devices have to be added to the app beforehand
before the database (or backup) is extracted.

Creating a backup
-----------------

The first step to do this is to extract a backup
or database from the Mi Home app.
The procedure is briefly described below,
but you may find the following links also useful:

- https://github.com/jghaanstra/com.xiaomi-miio/blob/master/docs/obtain_token.md
- https://github.com/homeassistantchina/custom_components/blob/master/doc/chuang_mi_ir_remote.md

Android
~~~~~~~

Start by installing the newest version of the Mi Home app from Google Play and
setting up your account. When the app asks you which server you want to use,
it's important to pick one that is also available in older versions of Mi
Home (we'll see why a bit later). U.S or china servers are OK, but the european
server is not supported by the old app. Then, set up your Xiaomi device with the
Mi Home app.

After the setup is completed, and the device has been connected to the Wi-Fi
network of your choice, it is necessary to downgrade the Mi Home app to some
version equal or below 5.0.19. As explained `here <https://github.com/jghaanstra/com.xiaomi-miio/blob/master/docs/obtain_token.md#method-3---obtain-mi-home-device-token-for-devices-that-hide-their-tokens-after-setup>`_
and `here <https://github.com/rytilahti/python-miio/issues/185>`_, newer versions
of the app do not download the token into the local database, which means that
we can't retrieve the token from the backup. You can find older versions of the
Mi Home app in `apkmirror <https://www.apkmirror.com/apk/xiaomi-inc/mihome/>`_.

Download, install and start up the older version of the Mi Home app. When the
app asks which server should be used, pick the same one you used with the newer
version of the app. Then, log into your account.

After this point, you are ready to perform the backup and extract the token.
Please note that it's possible that your device does not show under the old app.
As long as you picked the same server, it should be OK, and the token should
have been downloaded and stored into the database.

To do a backup of an Android app you need to have the developer mode active, and
your device has to be accessible with ``adb``.

.. TODO::
    Add a link how to check and enable the developer mode.
    This part of documentation needs your help!
    Please consider submitting a pull request to update this.

After you have connected your device to your computer,
and installed the Android developer tools,
you can use ``adb`` tool to create a backup.

.. code-block:: bash

    adb backup -noapk com.xiaomi.smarthome -f backup.ab

.. NOTE::
    Depending on your Android version you may need to insert a password
    and/or accept the backup, so check your phone at this point!

If everything went fine and you got a ``backup.ab`` file,
please continue to :ref:`token_extraction`.

Apple
~~~~~

Create a new unencrypted iOS backup to your computer. 
To do that you've to follow these steps:

- Connect your iOS device to the computer
- Open iTunes
- Click on your iOS device (sidebar left or icon on top navigation bar)
- In the Summary view check the following settings
    - Automatically Back Up: ``This Computer``
    - **Disable** ``Encrypt iPhone backup``
- Click ``Back Up Now``

When the backup is finished, download `iBackup Viewer <https://www.imactools.com/iphonebackupviewer/>`_ and follow these steps:

- Open iBackup Viewer
- Click on your newly created backup
- Click on the ``Raw Files`` icon (looks like a file tree)
- On the left column, search for ``AppDomain-com.xiaomi.mihome`` and select it
- Click on the search icon in the header
- Enter ``_mihome`` in the search field
- Select the ``Documents/0123456789_mihome.sqlite`` file (the one with the number prefixed)
- Click ``Export -> Selected…`` in the header and store the file

Now you've exported the SQLite database to your Mac and you can extract the tokens.

.. note::

    See also `jghaanstra's obtain token docs <https://github.com/jghaanstra/com.xiaomi-miio/blob/master/docs/obtain_token.md#ios-users>`_ for alternative ways.

.. _token_extraction:

Extracting tokens
-----------------

Now having extract either a backup or a database from the application,
the ``miio-extract-tokens`` can be used to extract the tokens from it.

At the moment extracting tokens from a backup (Android),
or from an extracted database (Android, Apple) are supported.

Encrypted tokens as `recently introduced on iOS devices <https://github.com/rytilahti/python-miio/issues/75>`_ will be automatically decrypted.
For decrypting Android backups the password has to be provided
to the tool with ``--password <password>``.

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

Extracting tokens manually
--------------------------

Run the following SQLite command:

.. code-block:: bash

    sqlite3 <path of *_mihome.sqlite database> "select ZNAME,ZLOCALIP,ZTOKEN from ZDEVICE"

You should get a list which looks like this:

.. code-block:: text

    Device 1|x.x.x.x|0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
    Device 2|x.x.x.x|0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
    Device 3|x.x.x.x|0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef

These are your device names, IP addresses and tokens. However, the tokens are encrypted and you need to decrypt them.
The command for decrypting the token manually is:

.. code-block:: bash

    echo '0: <YOUR 32 CHARACTER TOKEN>' | xxd -r -p | openssl enc -d -aes-128-ecb -nopad -nosalt -K 00000000000000000000000000000000

Environment variables for command-line tools
============================================

To simplify the use, instead of passing the IP and the token as a
parameter for the tool, you can simply set the following environment variables.
The following works for `mirobo`, for other tools you should consult
the documentation of corresponding tool.

.. code-block:: bash

    export MIROBO_IP=192.168.1.2
    export MIROBO_TOKEN=476e6b70343055483230644c53707a12
