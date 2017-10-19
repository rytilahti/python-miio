Getting started
---------------


Automatic token discovery
~~~~~~~~~~~~~~~~~~~~~~~~~

.. IMPORTANT::

    For some devices (e.g. the vacuum cleaner) the automatic discovery works only before the device has been connected over the app to your local wifi.
    This does not work starting from firmware version 3.3.9\_003077 onwards, in which case the procedure shown in creating_backup_ has to be used.

In order to use automatic token discovery, the device on which `python-miio` is run has to be connected over wifi to the device.
This involves usually reseting to device so that it will offer its initial setup network (e.g. rockrobo-XXXX in case of the vacuum).
The following command will execute the discovery process using the miIO protocol, which sometimes yields usable tokens.

::

    mirobo discover --handshake 1

which should return something similar to this:

::

    INFO:mirobo.vacuum:  IP 192.168.8.1: Xiaomi Mi Robot Vacuum - token: b'ffffffffffffffffffffffffffffffff'

If the value is as shown above, the vacuum has already been connected
and it needs a reset. Otherwise the token can be copied over and used
for controlling.


.. NOTE::
    For the Mi Robot Vacuum Cleaner with firmware 3.3.9\_003077
    or higher follow these steps to get the token:
    https://github.com/jghaanstra/com.xiaomi-miio/blob/master/docs/obtain\_token\_mirobot\_new.md
    (`another source <https://github.com/homeassistantchina/custom_components/blob/master/doc/chuang_mi_ir_remote.md>`__).

    This will also work for all other devices as long as the device has been bound with the Mi Home mobile application,
    and is therefore preferable way to attain the token.

.. _creating_backup:

Creating a backup
~~~~~~~~~~~~~~~~~

asdf

Extracting tokens from backups
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The package provides a command line tool ``miio-extract-tokens``` to extract tokens from Android backups and SQlite databases.
Please follow the above-mentioned procedure to retrieve a backup (Android) or a SQlite database (Android & Apple).
Encrypted tokens as recently introduced on iOS devices will be automatically decrypted.
For decrypting encrypted Android backups the password has to be given to the command with ``--password <password>``.

*Please feel free to submit pull requests to simplify this procedure!*

::

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

