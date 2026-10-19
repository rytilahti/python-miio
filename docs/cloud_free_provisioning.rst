.. _cloud_free_provisioning:

Cloud-free provisioning (stable local token)
********************************************

This page describes how to provision a Xiaomi miIO Wi-Fi device so that it can be
controlled locally **indefinitely and without a cloud account**, by preventing the
device from ever reaching Xiaomi's cloud (which otherwise re-keys the device token).

.. note::

    Verified on ``chuangmi.plug.m1`` (Marvell MW300, firmware ``1.4.5_2``). The
    technique is protocol-level and should apply to other miIO Wi-Fi devices that
    accept a ``country_domain`` during provisioning, but only the device above has
    been tested. Reports of other devices are welcome.

Background
==========

Every miIO command is authenticated with the 16-byte device token. The token is
disclosed during pairing, so it can be read then. However, on current firmware the
token is **re-keyed the first time the device reaches Xiaomi's cloud**. That is why a
token captured at pairing frequently stops working shortly after the device joins
Wi-Fi, and why obtaining the token via the cloud is otherwise necessary.

The technique
=============

``miIO.config_router`` — the account-free command used during pairing to hand the
device your Wi-Fi credentials — also accepts a ``country_domain`` field, from which
the firmware builds its cloud server name as ``<country_domain>.ot.io.mi.com``. Real
regions resolve; a **bogus region does not** (there is no wildcard record):

.. code-block:: text

    ot.io.mi.com     -> resolves
    us.ot.io.mi.com  -> resolves
    zz.ot.io.mi.com  -> NXDOMAIN

Provisioning with a bogus ``country_domain`` (e.g. ``zz``) therefore pins the device
to a cloud endpoint that is unresolvable on **any** network. The device never reaches
Xiaomi, so the token disclosed at pairing is never re-keyed and stays valid for local
control — even if the device otherwise has full internet access, and without any
router-level firewall rules.

How to
======

#. Factory-reset the device into pairing mode and connect your computer to the
   device's own Wi-Fi access point (its setup gateway is typically
   ``192.168.13.1``).
#. Read the token the device discloses while in pairing mode (for example with
   ``miiocli discover``, which prints the token when the device exposes it).
#. Send a single ``miIO.config_router`` with your Wi-Fi credentials and a bogus
   ``country_domain``:

   .. code-block:: python

       from miio import Device

       # 'token' is the value the device disclosed in pairing mode.
       dev = Device("192.168.13.1", token)
       dev.send(
           "miIO.config_router",
           {
               "ssid": "YourWiFi",
               "passwd": "YourPassword",
               "uid": 0,
               "country_domain": "zz",  # bogus region -> NXDOMAIN cloud
           },
       )

#. The device joins your Wi-Fi. Control it normally with the captured token:

   .. code-block:: bash

       miiocli device --ip <device-ip> --token <token> info

Evidence
========

In a controlled test, a device provisioned onto an internet-connected network
contacted ``*.ot.io.mi.com`` on UDP port ``8053`` and its captured token was rejected
within ~2 minutes. Repeating with ``country_domain=zz`` on the same
internet-connected network, a packet capture showed only failing DNS lookups and
**no** connection to port ``8053``, and the token continued to authenticate.

Caveats
=======

* The device can no longer be controlled by the Mi Home app and receives no cloud
  features or firmware updates — which is the intent.
* A factory reset clears the setting; re-run provisioning to obtain a fresh token.
* This does not weaken the device's authentication or expose the token; discovery
  still reports a zeroed token.

See also
========

A standalone reference implementation (pairing + local control) is available at
`miio-cloudfree <https://github.com/SahajJain01/miio-cloudfree>`__. The technique was
reported in `issue #2094 <https://github.com/rytilahti/python-miio/issues/2094>`__.
