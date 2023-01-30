Yeelight
========

.. NOTE::

    Only basic support for controlling Yeelight lights is implemented at the moment.

    You will likely want to use `python-yeelight <https://gitlab.com/stavros/python-yeelight>`_
    for controlling your lights.


Currently supported features:

-  Querying the status.
-  Turning on and off.
-  Changing brightness, colors (RGB and HSV), color temperature.
-  Changing internal settings (developer mode, saving settings on change)


Use ``miiocli yeelight --help``
for help on available commands and their parameters.

To extract the token from a backup of the official Yeelight app, refer to :ref:`yeelight_token_extraction`.

.. _yeelight_token_extraction:

Token extraction
----------------

In order to extract tokens from the Yeelight Android app,
you need to create a backup like shown below.

.. code-block:: bash

    adb backup -noapk com.yeelight.cherry -f backup.ab

If everything went fine and you got a ``backup.ab`` file,
from which you can extract the tokens with ``miio-extract-tokens`` as described in :ref:`token_extraction`.

.. code-block:: bash

    miio-extract-tokens /tmp/yeelight.ab --password a

    Unable to find miio database file apps/com.xiaomi.smarthome/db/miio2.db: "filename 'apps/com.xiaomi.smarthome/db/miio2.db' not found"
    INFO:miio.extract_tokens:Trying to read apps/com.yeelight.cherry/sp/miot.xml
    INFO:miio.extract_tokens:Reading tokens from Yeelight Android DB
    Yeelight Color Bulb
            Model: yeelink.light.color1
            IP address: 192.168.xx.xx
            Token: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
            MAC: F0:B4:29:xx:xx:xx
    Mi Bedside Lamp
            Model: yeelink.light.bslamp1
            IP address: 192.168.xx.xx
            Token: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
            MAC: 7C:49:EB:xx:xx:xx


Usage examples
--------------

Status reporting
~~~~~~~~~~~~~~~~

::

    $ miiocli yeelight --ip 192.168.xx.xx --token xxxx status
    Name:
    Power: False
    Brightness: 39
    Color mode: 1
    RGB: (255, 152, 0)
    HSV: None
    Temperature: None
    Developer mode: True
    Update default on change: True


.. NOTE::

    If you find a new command please let us know by creating a pull request
    or an issue, if you do not want to implement it on your own!


:py:class:`API <miio.integrations.yeelight.light>`
