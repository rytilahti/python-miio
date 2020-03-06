python-miio
===========

|PyPI version| |Build Status| |Coverage Status| |Docs| |Black| |Hound|

This library (and its accompanying cli tool) is used to interface with devices using Xiaomi's `miIO protocol <https://github.com/OpenMiHome/mihome-binary-protocol/blob/master/doc/PROTOCOL.md>`__.


Supported devices
-----------------

-  Xiaomi Mi Robot Vacuum V1, S5, M1S
-  Xiaomi Mi Home Air Conditioner Companion
-  Xiaomi Mi Air Purifier
-  Xiaomi Aqara Camera
-  Xiaomi Aqara Gateway (basic implementation, alarm, lights)
-  Xiaomi Mijia 360 1080p
-  Xiaomi Mijia STYJ02YM (Viomi)
-  Xiaomi Mi Smart WiFi Socket
-  Xiaomi Chuangmi Plug V1 (1 Socket, 1 USB Port)
-  Xiaomi Chuangmi Plug V3 (1 Socket, 2 USB Ports)
-  Xiaomi Smart Power Strip V1 and V2 (WiFi, 6 Ports)
-  Xiaomi Philips Eyecare Smart Lamp 2
-  Xiaomi Philips RW Read (philips.light.rwread)
-  Xiaomi Philips LED Ceiling Lamp
-  Xiaomi Philips LED Ball Lamp (philips.light.bulb)
-  Xiaomi Philips LED Ball Lamp White (philips.light.hbulb)
-  Xiaomi Philips Zhirui Smart LED Bulb E14 Candle Lamp
-  Xiaomi Philips Zhirui Bedroom Smart Lamp
-  Xiaomi Universal IR Remote Controller (Chuangmi IR)
-  Xiaomi Mi Smart Pedestal Fan V2, V3, SA1, ZA1, ZA3, ZA4, P5
-  Xiaomi Mi Air Humidifier V1, CA1, CB1, MJJSQ
-  Xiaomi Mi Water Purifier (Basic support: Turn on & off)
-  Xiaomi PM2.5 Air Quality Monitor V1, B1, S1
-  Xiaomi Smart WiFi Speaker
-  Xiaomi Mi WiFi Repeater 2
-  Xiaomi Mi Smart Rice Cooker
-  Xiaomi Smartmi Fresh Air System VA2 (zhimi.airfresh.va2), T2017 (dmaker.airfresh.t2017)
-  Yeelight lights (basic support, we recommend using `python-yeelight <https://gitlab.com/stavros/python-yeelight/>`__)
-  Xiaomi Mi Air Dehumidifier
-  Xiaomi Tinymu Smart Toilet Cover
-  Xiaomi 16 Relays Module
-  Xiaomi Xiao AI Smart Alarm Clock
-  Smartmi Radiant Heater Smart Version (ZA1 version)
-  Xiaomi Mi Smart Space Heater


*Feel free to create a pull request to add support for new devices as
well as additional features for supported devices.*


Getting started
---------------

Refer `the manual <https://python-miio.readthedocs.io>`__ for getting started.


Contributing
------------

We welcome all sorts of contributions from patches to add improvements or fixing bugs to improving the documentation.
To ease the process of setting up a development environment we have prepared `a short guide <https://python-miio.readthedocs.io/en/latest/new_devices.html>`__ for getting you started.


Home Assistant support
----------------------

-  `Xiaomi Mi Robot Vacuum <https://home-assistant.io/components/vacuum.xiaomi_miio/>`__
-  `Xiaomi Philips Light <https://home-assistant.io/components/light.xiaomi_miio/>`__
-  `Xiaomi Mi Air Purifier and Air Humidifier <https://home-assistant.io/components/fan.xiaomi_miio/>`__
-  `Xiaomi Smart WiFi Socket and Smart Power Strip <https://home-assistant.io/components/switch.xiaomi_miio/>`__
-  `Xiaomi Universal IR Remote Controller <https://home-assistant.io/components/remote.xiaomi_miio/>`__
-  `Xiaomi Mi Air Quality Monitor (PM2.5) <https://home-assistant.io/components/sensor.xiaomi_miio/>`__
-  `Xiaomi Aqara Gateway Alarm <https://home-assistant.io/components/alarm_control_panel.xiaomi_miio/>`__
-  `Xiaomi Mi Home Air Conditioner Companion <https://github.com/syssi/xiaomi_airconditioningcompanion>`__
-  `Xiaomi Mi WiFi Repeater 2 <https://www.home-assistant.io/components/device_tracker.xiaomi_miio/>`__
-  `Xiaomi Mi Smart Pedestal Fan <https://github.com/syssi/xiaomi_fan>`__
-  `Xiaomi Mi Smart Rice Cooker <https://github.com/syssi/xiaomi_cooker>`__
-  `Xiaomi Raw Sensor <https://github.com/syssi/xiaomi_raw>`__


.. |PyPI version| image:: https://badge.fury.io/py/python-miio.svg
   :target: https://badge.fury.io/py/python-miio
.. |Build Status| image:: https://travis-ci.org/rytilahti/python-miio.svg?branch=master
   :target: https://travis-ci.org/rytilahti/python-miio
.. |Coverage Status| image:: https://coveralls.io/repos/github/rytilahti/python-miio/badge.svg?branch=master
   :target: https://coveralls.io/github/rytilahti/python-miio?branch=master
.. |Docs| image:: https://readthedocs.org/projects/python-miio/badge/?version=latest
   :alt: Documentation status
   :target: https://python-miio.readthedocs.io/en/latest/?badge=latest
.. |Hound| image:: https://img.shields.io/badge/Reviewed_by-Hound-8E64B0.svg
   :alt: Hound
   :target: https://houndci.com
.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
