python-miio
===========

|PyPI version| |Build Status| |Code Health| |Coverage Status|

This library (and its accompanying cli tool) is used to interface with devices using Xiaomi's `miIO protocol <https://github.com/OpenMiHome/mihome-binary-protocol/blob/master/doc/PROTOCOL.md>`__.

.. NOTE::
   The project has been recently renamed to `python-miio`.
   Althought the `mirobo` python package (as well as the console tool with the same name) are still available,
   the users of the library are encouraged to start using the `miio` package.
   The shipped console tools (and the API) are expected to stay backwards-compatible for the near future.


Supported devices
-----------------

-  :py:class:`Xiaomi Mi Robot Vacuum <miio.vacuum>`
-  :py:class:`Xiaomi Mi Air Purifier Pro & Air Purifier 2 <miio.AirPurifier>`
-  :py:class:`Xiaomi Mi Smart WiFi Socket <miio.Plug>`
-  :py:class:`Xiaomi Mi Smart Socket Plug (1 Socket, 1 USB Port) <miio.Plug>`
-  :py:class:`Xiaomi Smart Power Strip (WiFi, 6 Ports) <miio.Strip>`
-  :py:class:`Xiaomi Philips Eyecare Smart Lamp 2 <miio.PhilipsEyecare>`
-  :py:class:`Xiaomi Philips LED Ceiling Lamp <miio.Ceil>`
-  Xiaomi Philips LED Ball Lamp
-  :py:class:`Xiaomi Universal IR Remote Controller (Chuang Mi IR) <miio.ChuangmiIr>`
-  :py:class:`Xiaomi Mi Smart Fan <miio.Fan>`
-  :py:class:`Xiaomi Mi Air Humidifier <miio.AirHumidifier>`
-  :py:class:`Xiaomi Mi Water Purifier (Basic support: Turn on & off) <miio.WaterPurifier>`
-  :py:class:`Xiaomi PM2.5 Air Quality Monitor <miio.AirQualityMonitor>`
-  :py:class:`Xiaomi Smart Wifi Speaker <miio.WifiSpeaker>` (untested and incomplete, please `feel free to help improve the support <https://github.com/rytilahti/python-miio/issues/69>`__)
-  :py:class:`Yeelight light bulbs <miio.Yeelight>` (only a very rudimentary support, use `python-yeelight <https://gitlab.com/stavros/python-yeelight/>`__ for a more complete support)

*Feel free to create a pull request to add support for new devices as
well as additional features for supported devices.*

Adding support for other devices
--------------------------------

The `miio javascript library <https://github.com/aholstenson/miio>`__
contains some hints on devices which could be supported, however, the
Xiaomi Smart Home gateway (`Home Assistant
component <https://github.com/lazcad/homeassistant>`__ already work in
progress) as well as Yeelight bulbs are currently not in the scope of
this project.


Getting started
===============

As long as the device is in the same network, ``mirobo discover`` can be
used to check for its support status.

To be able to communicate with supported devices its IP address and an
encryption token must be known. The token can be obtained either by
extracting it from the database of the Mi Home application, or by using
the automatic discovery.


Usage
-----

To simplify the use, instead of passing the IP and the token as a
parameter for the tool, you can simply set the following environment
variables.

::

    export MIROBO_IP=192.168.1.2
    export MIROBO_TOKEN=476e6b70343055483230644c53707a12

After that verify that the connection is working by running the command
without parameters, you should be presented a status report from the
vacuum.

Use ``mirobo --help`` to see available commands and description about
what they do. ``--debug`` option can be used to let it show raw JSON
data being communicated.


Home Assistant support
----------------------

-  `Xiaomi Mi Robot
   Vacuum <https://home-assistant.io/components/vacuum.xiaomi_miio/>`__
-  `Xiaomi Philips
   Light <https://home-assistant.io/components/light.xiaomi_miio/>`__
-  `Xiaomi Mi Air
   Purifier <https://github.com/syssi/xiaomi_airpurifier>`__
-  `Xiaomi WiFi Plug <https://github.com/syssi/xiaomiplug>`__
-  `Xiaomi Universal IR Remote
   Controller <https://github.com/syssi/chuangmi_ir>`__

.. |PyPI version| image:: https://badge.fury.io/py/python-miio.svg
   :target: https://badge.fury.io/py/python-miio
.. |Build Status| image:: https://travis-ci.org/rytilahti/python-miio.svg?branch=0.2.0
   :target: https://travis-ci.org/rytilahti/python-miio
.. |Code Health| image:: https://landscape.io/github/rytilahti/python-miio/master/landscape.svg?style=flat
   :target: https://landscape.io/github/rytilahti/python-miio/master
.. |Coverage Status| image:: https://coveralls.io/repos/github/rytilahti/python-miio/badge.svg?branch=master
   :target: https://coveralls.io/github/rytilahti/python-miio?branch=master

History
-------
This project was started to allow controlling locally available Xiaomi
Vacuum cleaner robot with Python (hence the old name ``python-mirobo``),
however, thanks to contributors it has been extended to allow
controlling other Xiaomi devices using the same protocol `miIO protocol <https://github.com/OpenMiHome/mihome-binary-protocol>`__.
(`another source for vacuum-specific
documentation <https://github.com/marcelrv/XiaomiRobotVacuumProtocol>`__)

First and foremost thanks for the nice people over `ioBroker
forum <http://forum.iobroker.net/viewtopic.php?f=23&t=4898>`__ who
figured out the encryption to make this library possible.
Furthermore thanks goes to contributors of this project who have helped to extend this to cover not only the vacuum cleaner.
