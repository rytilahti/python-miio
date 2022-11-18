Troubleshooting
===============

This page lists some known issues and potential solutions.
If you are having problems with incorrectly working commands or missing features,
please refer to :ref:`new_devices` for information how to analyze the device traffic.

.. contents:: Contents
   :local:


Discover devices across subnets
-------------------------------

Discovering across different subnets may fail for some devices with the following exception:

.. code-block:: text

    miio.exceptions.DeviceException: Unable to discover the device x.x.x.x

This behaviour has been experienced on the following device types:

- Xiaomi Zhimi Humidifier (aka ``zhimi.humidifier.v1``)
- Xiaomi Smartmi Evaporative Humidifier 2 (aka ``zhimi.humidifier.ca1``)
- Xiaomi IR Remote (aka ``chuangmi_ir``)
- RoboRock S7 (aka ``roborock.vacuum.a15``)
- RoboRock S7 MaxV Ultra (aka ``roborock.vacuum.a27``)

It's currently unclear if this is a bug or a security feature of the Xiaomi device.

.. note::

    The root cause is the source address in the UDP packet. The device won't react/respond to the miIO request, in case the source address of the UDP packet doesn't belong to the subnet of the device itself. This behaviour was experienced and described in `github issue #422 <https://github.com/rytilahti/python-miio/issues/422>`_.

Fortunately there are some workarounds to get the communication working.

The most obvious one would be placing the miIO client & MI device in the same subnet.
You can also dual-home your client and put it in multiple subnets.
This can be achieved either physically (e.g. multiple ethernet cables) or virtually (multiple VLAN's).

.. hint::

    You might have had your reasons for multiple subnets and they're probably security-related. If so, remember to configure a local firewall on your client so that incoming connections from untrusted subnets are restricted.

If you're in control of the router in between, then you have one more chance to get the communication up & running.
You can configure IP masquearding on the outgoing routing interface for the subnet where the MI device resides.
IP masquerading (NAT) basically changes the source address in the UDP packet to the IP address of the
outbound routing interface.

.. note::

    Read more about `Network address translation on Wikipedia <https://en.wikipedia.org/wiki/Network_address_translation>`_.


Intermittent connection issues, timeouts (Xiaomi Vacuum)
--------------------------------------------------------

Blocking the network access from vacuums is known to cause connectivity problems, presenting themselves as connection timeouts (discussed in `github issue #92 <https://github.com/rytilahti/python-miio/issues/92>`_):

.. code-block:: text

    mirobo.device.DeviceException: Unable to discover the device x.x.x.x

The root cause lies in the software running on the device, which will hang when it is unable to receive responses.
The connectivity will get restored by device's internal watchdog restarting the service (``miio_client``).

.. hint::

    If you want to keep your device out from the Internet, use REJECT instead of DROP in your firewall confinguration.


Roborock Vacuum not detected
----------------------------

It seems that a Roborock vacuum connected through the Roborock app (and not the Xiaomi Home app) won't allow control over local network,
 even with a valid token, leading to the following exception:

.. code-block:: text

    mirobo.device.DeviceException: Unable to discover the device x.x.x.x

Resetting the device's wifi and pairing it again with the Xiaomi Home app should solve the issue.

.. hint::

    A new pairing process will generate a new token. You will have to extract it as your previous one won't be valid anymore.
