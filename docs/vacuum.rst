Vacuum
======

Following features of the vacuum cleaner are currently supported:

-  Starting, stopping, pausing, locating.
-  Controlling the fan speed.
-  Fetching the current status.
-  Fetching and reseting the state of consumables.
-  Fetching and setting the schedules.
-  Setting and querying the timezone.
-  Installing sound packs.
-  Installing firmware updates.
-  Manual control of the robot. **Patches for a nicer API are very welcome.**

Use :ref:`mirobo --help <HelpOutput>`
for help on available commands and their parameters.

Usage examples
--------------

Status reporting
~~~~~~~~~~~~~~~~

::

    $ mirobo
    State: Charging
    Battery: 100
    Fanspeed: 60
    Cleaning since: 0:00:00
    Cleaned area: 0.0 m²
    DND enabled: 0
    Map present: 1
    in_cleaning: 0

Start cleaning
~~~~~~~~~~~~~~

::

    $ mirobo start
    Starting cleaning: 0

Return home
~~~~~~~~~~~

::

    $ mirobo home
    Requesting return to home: 0

Setting the fanspeed
~~~~~~~~~~~~~~~~~~~~

::

    $ mirobo fanspeed 30
    Setting fan speed to 30

State of consumables
~~~~~~~~~~~~~~~~~~~~

::

    $ mirobo consumables
    main: 9:24:48, side: 9:24:48, filter: 9:24:48, sensor dirty: 1:27:12

Schedule information
~~~~~~~~~~~~~~~~~~~~

::

    $ mirobo timer
    Timer #0, id 1488667794112 (ts: 2017-03-04 23:49:54.111999)
      49 22 * * 6
      At 14:49 every Saturday
    Timer #1, id 1488667777661 (ts: 2017-03-04 23:49:37.661000)
      49 21 * * 3,4,5,6
      At 13:49 every Wednesday, Thursday, Friday and Saturday
    Timer #2, id 1488667756246 (ts: 2017-03-04 23:49:16.246000)
      49 20 * * 0,1,2
      At 12:49 every Sunday, Monday and Tuesday
    Timer #3, id 1488667742238 (ts: 2017-03-04 23:49:02.237999)
      49 19 * * 0,6
      At 11:49 every Sunday and Saturday
    Timer #4, id 1488667726378 (ts: 2017-03-04 23:48:46.378000)
      48 18 * * 1,2,3,4,5
      At 10:48 every Monday, Tuesday, Wednesday, Thursday and Friday
    Timer #5, id 1488667715725 (ts: 2017-03-04 23:48:35.724999)
      48 17 * * 0,1,2,3,4,5,6
      At 09:48 every Sunday, Monday, Tuesday, Wednesday, Thursday, Friday and Saturday
    Timer #6, id 1488667697356 (ts: 2017-03-04 23:48:17.355999)
      48 16 5 3 *
      At 08:48 on the 5th of March

Adding a new timer

::

    $ mirobo timer add --cron '* * * * *'

Activating/deactivating an existing timer, use ``mirobo timer`` to get
the required id.

::

    $ mirobo timer update <id> [--enable|--disable]

Deleting a timer

::

    $ mirobo timer delete <id>

Cleaning history
~~~~~~~~~~~~~~~~

::

    $ mirobo cleaning-history
    Total clean count: 43
    Clean #0: 2017-03-05 19:09:40-2017-03-05 19:09:50 (complete: False, unknown: 0)
      Area cleaned: 0.0 m²
      Duration: (0:00:00)
    Clean #1: 2017-03-05 16:17:52-2017-03-05 17:14:59 (complete: False, unknown: 0)
      Area cleaned: 32.16 m²
      Duration: (0:23:54)


Sounds
~~~~~~

To get information about current sound settings:

::

    mirobo sound


You can use dustcloud's `audio generator`_ to create your own language packs,
which will handle both generation and encrypting the package for you.

There are two ways to install install sound packs:

1. Install by using self-hosting server, where you just need to point the sound pack you want to install.

::

    mirobo install-sound my_sounds.pkg

2. Install from an URL, in which case you need to pass the md5 hash of the file as a second parameter.

::

    mirobo install-sound http://10.10.20.1:8000/my_sounds.pkg b50cfea27e52ebd5f46038ac7b9330c8

`--sid` can be used to select the sound ID (SID) for the new file,
using an existing SID will overwrite the old.

If the automatic detection of the IP address for self-hosting server is not working,
you can override this by using `--ip` option.


.. _audio generator: https://github.com/dgiese/dustcloud/tree/master/devices/xiaomi.vacuum/audio_generator

Firmware update
~~~~~~~~~~~~~~~

This can be useful if you want to downgrade or do updates without connecting to the cloud,
or if you want to use a custom rooted firmware.
`Dustcloud project <https://github.com/dgiese/dustcloud>`_ provides a way to generate your own firmware images,
and they also have `a firmware archive <https://github.com/dgiese/dustcloud/tree/master/devices/xiaomi.vacuum.gen1/firmware>`_
for original firmwares.

.. WARNING::
    Updating firmware should not be taken lightly even when the device will automatically roll-back
    to the previous version when failing to do an update.

    Using custom firmwares may hamper the functionality of your vacuum,
    and it is unknown how the factory reset works in these cases.

This feature works similarly to the sound updates,
so passing a local file will create a self-hosting server
and updating from an URL requires you to pass the md5 hash of the file.

::

    mirobo update-firmware v11_003094.pkg


DND functionality
~~~~~~~~~~~~~~~~~

To disable:

::

    mirobo dnd off

To enable (dnd 22:00-0600):

::

    mirobo dnd on 22 0 6 0

Carpet mode
~~~~~~~~~~~

Carpet mode increases the suction when encountering a carpet.
The optional parameters (when using miiocli) are unknown and set as
they were in the original firmware.

To enable:

::

    mirobo carpet-mode 1 (or any other true-value, such as 'true')


To disable:

::

    mirobo carpet-mode 0


Raw commands
~~~~~~~~~~~~

It is also possible to run raw commands, which can be useful
 for testing new unknown commands or if you want to have full access
 to what is being sent to the device:

::

    mirobo raw-command app_start

or with parameters (same as above dnd on):

::

    mirobo raw-command set_dnd_timer '[22,0,6,0]'

The input is passed as it is to the device as the `params` value,
so it is also possible to pass dicts.

.. NOTE::

    If you find a new command please let us know by creating a pull request
    or an issue, if you do not want to implement it on your own!

.. _HelpOutput:

`mirobo --help`
~~~~~~~~~~~~~~~

.. click:: miio.vacuum_cli:cli
   :prog: mirobo
   :show-nested:

:py:class:`API <miio.vacuum>`
