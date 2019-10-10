python-miio
===========

|PyPI version| |Build Status| |Coverage Status| |Docs| |Hound|

This library (and its accompanying cli tool) is used to interface with devices using Xiaomi's `miIO protocol <https://github.com/OpenMiHome/mihome-binary-protocol/blob/master/doc/PROTOCOL.md>`__.


Supported devices
-----------------

-  :doc:`Xiaomi Mi Robot Vacuum <vacuum>` V1, S5, M1S (:class:`miio.vacuum`)
-  Xiaomi Mi Home Air Conditioner Companion (:class:`miio.airconditioningcompanion`)
-  Xiaomi Mi Air Purifier (:class:`miio.airpurifier`)
-  Xiaomi Aqara Camera (:class:`miia.aqaracamera`)
-  Xiaomi Mijia 360 1080p (:class`miio.chuangmi_camera`)
-  :doc:`Xiaomi Mi Smart WiFi Socket <plug>` (:class:`miio.chuangmi_plug`)
-  :doc:`Xiaomi Chuangmi Plug V1 (1 Socket, 1 USB Port) <plug>` (:class:`miio.chuangmi_plug`)
-  :doc:`Xiaomi Chuangmi Plug V3 (1 Socket, 2 USB Ports) <plug>` (:class:`miio.chuangmi_plug`)
-  Xiaomi Smart Power Strip V1 and V2 (WiFi, 6 Ports) (:class:`miio.powerstrip`)
-  :doc:`Xiaomi Philips Eyecare Smart Lamp 2 <eyecare>` (:class:`miio.philips_eyecare`)
-  :doc:`Xiaomi Philips LED Ceiling Lamp <ceil>` (:class:`miio.ceil`)
-  Xiaomi Philips LED Ball Lamp (:class:`miio.philips_bulb`)
-  Xiaomi Philips Zhirui Smart LED Bulb E14 Candle Lamp (:class:`miio.philips_bulb`)
-  Xiaomi Philips Zhirui Bedroom Smart Lamp (:class:`miio.philips_moonlight`)
-  Xiaomi Universal IR Remote Controller (Chuangmi IR) (:class:`miio.chuangmi_ir`)
-  Xiaomi Mi Smart Pedestal Fan V2, V3, SA1, ZA1, ZA3, ZA4, P5 (:class:`miio.fan`)
-  Xiaomi Mi Air Humidifier V1, CA1, CB1 (:class:`miio.airhumidifier`)
-  Xiaomi Mi Water Purifier (Basic support: Turn on & off) (:class:`miio.waterpurifier`)
-  Xiaomi PM2.5 Air Quality Monitor V1, B1, S1 (:class:`miio.airqualitymonitor`)
-  Xiaomi Smart WiFi Speaker (:class:`miio.wifispeaker`)
-  Xiaomi Mi WiFi Repeater 2 (:class:`miio.wifirepeater`)
-  Xiaomi Mi Smart Rice Cooker (:class:`miio.cooker`)
-  Xiaomi Smartmi Fresh Air System (:class:`miio.airfresh`)
-  :doc:`Yeelight light bulbs <yeelight>` (:class:`miio.yeelight`) (only a very rudimentary support, use `python-yeelight <https://gitlab.com/stavros/python-yeelight/>`__ for a more complete support)
-  Xiaomi Mi Air Dehumidifier (:class:`miio.airdehumidifier`)
-  Xiaomi Tinymu Smart Toilet Cover (:class:`miio.toiletlid`)
-  Xiaomi 16 Relays Module (:class:`miio.pwzn_relay`)
-  Xiaomi Xiao AI Smart Alarm Clock (:class:`miio.alarmclock`)

*Feel free to create a pull request to add support for new devices as
well as additional features for supported devices.*


Getting started
---------------

Refer `the manual <https://python-miio.readthedocs.io>`__ for getting started.


Home Assistant support
----------------------

-  `Xiaomi Mi Robot Vacuum <https://home-assistant.io/components/vacuum.xiaomi_miio/>`__
-  `Xiaomi Philips Light <https://home-assistant.io/components/light.xiaomi_miio/>`__
-  `Xiaomi Mi Air Purifier and Air Humidifier <https://home-assistant.io/components/fan.xiaomi_miio/>`__
-  `Xiaomi Smart WiFi Socket and Smart Power Strip <https://home-assistant.io/components/switch.xiaomi_miio/>`__
-  `Xiaomi Universal IR Remote Controller <https://home-assistant.io/components/remote.xiaomi_miio/>`__
-  `Xiaomi Mi Air Quality Monitor (PM2.5) <https://home-assistant.io/components/sensor.xiaomi_miio/>`__
-  `Xiaomi Mi Home Air Conditioner Companion <https://github.com/syssi/xiaomi_airconditioningcompanion>`__
-  `Xiaomi Mi WiFi Repeater 2 <https://www.home-assistant.io/components/device_tracker.xiaomi_miio/>`__
-  `Xiaomi Mi Smart Pedestal Fan <https://github.com/syssi/xiaomi_fan>`__
-  `Xiaomi Mi Smart Rice Cooker <https://github.com/syssi/xiaomi_cooker>`__
-  `Xiaomi Raw Sensor <https://github.com/syssi/xiaomi_raw>`__


.. |PyPI version| image:: https://badge.fury.io/py/python-miio.svg
   :target: https://badge.fury.io/py/python-miio
.. |Build Status| image:: https://travis-ci.org/rytilahti/python-miio.svg?branch=master
   :target: https://travis-ci.org/rytilahti/python-miio
.. |Code Health| image:: https://landscape.io/github/rytilahti/python-miio/master/landscape.svg?style=flat
   :target: https://landscape.io/github/rytilahti/python-miio/master
.. |Coverage Status| image:: https://coveralls.io/repos/github/rytilahti/python-miio/badge.svg?branch=master
   :target: https://coveralls.io/github/rytilahti/python-miio?branch=master
.. |Docs| image:: https://readthedocs.org/projects/python-miio/badge/?version=latest
   :alt: Documentation status
   :target: https://python-miio.readthedocs.io/en/latest/?badge=latest
.. |Hound| image:: https://img.shields.io/badge/Reviewed_by-Hound-8E64B0.svg
   :alt: Hound
   :target: https://houndci.com
