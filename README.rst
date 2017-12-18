python-miio
===========

|PyPI version| |Build Status| |Code Health| |Coverage Status|

This library (and its accompanying cli tool) is used to interface with devices using Xiaomi's `miIO protocol <https://github.com/OpenMiHome/mihome-binary-protocol/blob/master/doc/PROTOCOL.md>`__.

.. NOTE::
   The project has been recently renamed to `python-miio`.
   Although the `mirobo` python package (as well as the console tool with the same name) are still available,
   the users of the library are encouraged to start using the `miio` package.
   The shipped console tools (and the API) are expected to stay backwards-compatible for the near future.


Supported devices
-----------------

-  :doc:`Xiaomi Mi Robot Vacuum <vacuum>` (:class:`miio.vacuum`)
-  Xiaomi Mi Home Air Conditioner Companion (:class:`miio.airconditioningcompanion`)
-  Xiaomi Mi Air Purifier Pro & Air Purifier 2 (:class:`miio.airpurifier`)
-  :doc:`Xiaomi Mi Smart WiFi Socket <plug>` (:class:`miio.plug`)
-  :doc:`Xiaomi Mi Smart Socket Plug (1 Socket, 1 USB Port) <plug>` (:class:`miio.plug`)
-  Xiaomi Smart Power Strip (WiFi, 6 Ports) (:class:`miio.powerstrip`)
-  :doc:`Xiaomi Philips Eyecare Smart Lamp 2 <eyecare>` (:class:`miio.philips_eyecare`)
-  :doc:`Xiaomi Philips LED Ceiling Lamp <ceil>` (:class:`miio.ceil`)
-  Xiaomi Philips LED Ball Lamp (:class:`miio.philips_bulb`)
-  Xiaomi Universal IR Remote Controller (Chuang Mi IR) (:class:`miio.chuangmi_ir`)
-  Xiaomi Mi Smart Fan (:class:`miio.fan`)
-  Xiaomi Mi Air Humidifier (:class:`miio.airhumidifier`)
-  Xiaomi Mi Water Purifier (Basic support: Turn on & off) (:class:`miio.waterpurifier`)
-  Xiaomi PM2.5 Air Quality Monitor (:class:`miio.airqualitymonitor`)
-  Xiaomi Smart Wifi Speaker (:class:`miio.wifispeaker`) (incomplete, please `feel free to help improve the support <https://github.com/rytilahti/python-miio/issues/69>`__)
-  Yeelight light bulbs (:class:`miio.yeelight`) (only a very rudimentary support, use `python-yeelight <https://gitlab.com/stavros/python-yeelight/>`__ for a more complete support)

*Feel free to create a pull request to add support for new devices as
well as additional features for supported devices.*


Getting started
---------------

Refer `the manual <https://python-miio.readthedocs.io>`__ for getting started.


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
.. |Build Status| image:: https://travis-ci.org/rytilahti/python-miio.svg?branch=master
   :target: https://travis-ci.org/rytilahti/python-miio
.. |Code Health| image:: https://landscape.io/github/rytilahti/python-miio/master/landscape.svg?style=flat
   :target: https://landscape.io/github/rytilahti/python-miio/master
.. |Coverage Status| image:: https://coveralls.io/repos/github/rytilahti/python-miio/badge.svg?branch=master
   :target: https://coveralls.io/github/rytilahti/python-miio?branch=master
