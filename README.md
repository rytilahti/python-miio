# Python-mirobo

This project is an on-going effort to allow controlling locally available Xiaomi Vacuum cleaner robot with Python.
It is currently as its very early stages with lots of things being not implemented, so feel free to create pull requests
and report new missing functionality.

Thanks for the nice people over [ioBroker forum](http://forum.iobroker.net/viewtopic.php?f=23&t=4898) who figured out the encryption to make this possible.

# Features

* Basic functionality, including starting, stopping, pausing, locating.
* Controlling the fan speed.
* Fetching schedule, status, state of consumables.

## Not yet implemented

* Setting the clock
* Setting schedules

# Installation

The easiest way to install the package is to use pip: ```pip install python-mirobo```

# Getting started

To be able to communicate with the vacuum one needs to have its IP address as well as an encryption token.
This token is only attainable before the device has been connected over the app to your local wifi.

In order to fetch the token, reset the robot, connect to its the network its announcing (rockrobo-XXXX)
and run the following command:

```
mirobo discover
```

which should return something similar to this:

```
INFO:mirobo.vacuum:  IP 192.168.8.1: Xiaomi Mi Robot Vacuum - token: b'ffffffffffffffffffffffffffffffff'
```

If the value is as shown above, the vacuum has already been connected and it needs a reset.

# Usage

To simplify the use, instead of passing the IP and the token as a parameter for the tool,
you can simply set the following environment variables.

```
export MIROBO_IP=192.168.1.2
export MIROBO_TOKEN=476e6b70343055483230644c53707a12
```

After that verify that the connection is working by running the command withour parameters,
you should be presented a status report from the vacuum.

Use ```mirobo --help``` to see available commands and description about what they do.
```--debug``` option can be used to let it show raw JSON data being communicated.

## DND functionality

To disable:
```
mirobo dnd off
```

To enable (dnd 22:00-0600):
```
mirobo dnd on 22 0 6 0
```

It is also possible to run raw commands for testing:

```
mirobo raw_command app_start
```

or with parameters (same as above dnd on):
```
mirobo raw_command set_dnd_timer '[22,0,6,0]'
```

If you find a new command please let us know by creating a pull request or an issue, if you
do not want to implement it yourself!

# Home Assistant support

There is also a very rudimentary component for Home Assistant. In its current state it is more of a placeholder,
therefore you should know how to install it if you want to use it. Later on when the interface gets cleaned up
usage instructions will be added here.

An example configuration:
```
- platform: mirobo
  name: 'name of the robot'
  host: 192.168.1.2
  token: your-token-here
```

# Usage examples

## Status reporting

```
$ mirobo
State: Charging
Battery: 100
Fanspeed: 60
Cleaning since: 0:00:00
Cleaned area: 0.0 m²
DND enabled: 0
Map present: 1
in_cleaning: 0
```

## Start cleaning

```
$ mirobo start
Starting cleaning: 0
```

## Return home

```
$ mirobo home
Requesting return to home: 0
```

## Setting the fanspeed

```
$ mirobo fanspeed 30
Setting fan speed to 30
0
```

## State of consumables

```
$ mirobo consumables
main: 9:24:48, side: 9:24:48, filter: 9:24:48, sensor dirty: 1:27:12
```

## Schedule information

```
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
```

## Cleaning history

```
$ mirobo cleaning_history
Total clean count: 43
Clean #0: 2017-03-05 19:09:40-2017-03-05 19:09:50 (complete: False, unknown: 0)
  Area cleaned: 0.0 m²
  Duration: (0:00:00)
Clean #1: 2017-03-05 16:17:52-2017-03-05 17:14:59 (complete: False, unknown: 0)
  Area cleaned: 32.16 m²
  Duration: (0:23:54)

```
