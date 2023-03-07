:orphan:


.. _legacy_token_extraction:

Legacy methods for obtaining tokens
***********************************

This page describes several ways to extract device tokens,
both with and without cloud access.

.. note::

    You generally want to use the :ref:`miiocli cloud command <obtaining_tokens>` to obtain tokens.
    These methods are listed here just for historical reference and may not work anymore.

.. _logged_tokens:

Tokens from Mi Home logs
========================

The easiest way to obtain tokens yourself is to browse through log files of the Mi Home
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

* https://github.com/jghaanstra/com.xiaomi-miio/blob/master/docs/obtain_token.md
* https://github.com/homeassistantchina/custom_components/blob/master/doc/chuang_mi_ir_remote.md

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
and `in github issue #185 <https://github.com/rytilahti/python-miio/issues/185>`_, newer versions
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

#. Connect your iOS device to the computer
#. Open iTunes
#. Click on your iOS device (sidebar left or icon on top navigation bar)
#. In the Summary view check the following settings
    * Automatically Back Up: ``This Computer``
    * **Disable** ``Encrypt iPhone backup``
#. Click ``Back Up Now``

When the backup is finished, download `iBackup Viewer <https://www.imactools.com/iphonebackupviewer/>`_ and follow these steps:

#. Open iBackup Viewer
#. Click on your newly created backup
#. Click on the ``Raw Files`` icon (looks like a file tree)
#. On the left column, search for ``AppDomain-com.xiaomi.mihome`` and select it
#. Click on the search icon in the header
#. Enter ``_mihome`` in the search field
#. Select the ``Documents/0123456789_mihome.sqlite`` file (the one with the number prefixed)
#. Click ``Export -> Selected…`` in the header and store the file

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

.. code-block:: bash

    $ miio-extract-tokens backup.ab
    Opened backup/backup.ab
    Extracting to /tmp/tmpvbregact
    Reading tokens from Android DB
    room1
            Model: yeelink.light.color1
            IP address: 192.168.XXX.XXX
            Token: 4679442a069f09883XXX
            MAC: F0:B4:29:XX:XX:XX
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

.. _rooted_tokens:

Tokens from rooted device
=========================

If a device is rooted via `dustcloud <https://github.com/dgiese/dustcloud>`_ (e.g. for running the cloud-free control webinterface `Valetudo <https://valetudo.cloud/>`_), the token can be extracted by connecting to the device via SSH and reading the file: :code:`printf $(cat /mnt/data/miio/device.token) | xxd -p`
