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
