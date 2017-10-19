Vacuum
======

Following features of the vacuum cleaner are currently supported:

-  Starting, stopping, pausing, locating.
-  Controlling the fan speed.
-  Fetching status and state of consumables. **Resetting consumable state
   is not currently implemented, patches welcome!**
-  Fetching and setting the schedules.
-  Setting and querying the timezone.
-  Manual control of the robot. **Patches for a nicer API are very welcome.**

Use ``mirobo --help`` for help on available commands and their parameters.

:py:class:`API <miio.Vacuum>`

DND functionality
~~~~~~~~~~~~~~~~~

To disable:

::

    mirobo dnd off

To enable (dnd 22:00-0600):

::

    mirobo dnd on 22 0 6 0

It is also possible to run raw commands for testing:

::

    mirobo raw_command app_start

or with parameters (same as above dnd on):

::

    mirobo raw_command set_dnd_timer '[22,0,6,0]'

If you find a new command please let us know by creating a pull request
or an issue, if you do not want to implement it on your own!

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

    $ mirobo cleaning_history
    Total clean count: 43
    Clean #0: 2017-03-05 19:09:40-2017-03-05 19:09:50 (complete: False, unknown: 0)
      Area cleaned: 0.0 m²
      Duration: (0:00:00)
    Clean #1: 2017-03-05 16:17:52-2017-03-05 17:14:59 (complete: False, unknown: 0)
      Area cleaned: 32.16 m²
      Duration: (0:23:54)