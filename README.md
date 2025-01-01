<h2 align="center">python-miio</h2>

[![Chat](https://img.shields.io/matrix/python-miio-chat:matrix.org)](https://matrix.to/#/#python-miio-chat:matrix.org)
[![PyPI
version](https://badge.fury.io/py/python-miio.svg)](https://badge.fury.io/py/python-miio)
[![PyPI
downloads](https://img.shields.io/pypi/dw/python-miio)](https://pypi.org/project/python-miio/)
[![Build
Status](https://github.com/rytilahti/python-miio/actions/workflows/ci.yml/badge.svg)](https://github.com/rytilahti/python-miio/actions/workflows/ci.yml)
[![Coverage
Status](https://codecov.io/gh/rytilahti/python-miio/branch/master/graph/badge.svg?token=lYKWubxkLU)](https://codecov.io/gh/rytilahti/python-miio)
[![Documentation status](https://readthedocs.org/projects/python-miio/badge/?version=latest)](https://python-miio.readthedocs.io/en/latest/?badge=latest)

This library (and its accompanying cli tool, `miiocli`) can be used to control devices using Xiaomi's
[miIO](https://github.com/OpenMiHome/mihome-binary-protocol/blob/master/doc/PROTOCOL.md)
and MIoT protocols.

This is a voluntary, community-driven effort and is not affiliated with any of the companies whose devices are supported by this library.
Issue reports and pull requests are welcome, see [contributing](#contributing)!

---

The full documentation is available at [python-miio.readthedocs.io](https://python-miio.readthedocs.io/en/latest/).

---

* [Installation](#installation)
* [Getting started](#getting-started)
* [Controlling modern (MIoT) devices](#controlling-modern-miot-devices)
* [Controlling older (miIO) devices](#controlling-older-miio-devices)
* [Troubleshooting](#troubleshooting)
* [API usage](#api-usage)
* [Contributing](#contributing)
* [Simulators](#simulators)
* [Supported devices](#supported-devices)
* [Projects using this library](#projects-using-this-library)
* [Other related projects](#other-related-projects)

---

## Installation

The most recent release can be installed using `pip`:

    pip install python-miio

Alternatively, you can install the latest development version from GitHub:

    pip install git+https://github.com/rytilahti/python-miio.git

**This project is currently ongoing [a major refactoring effort](https://github.com/rytilahti/python-miio/issues/1114).
If you are interested in controlling modern (MIoT) devices, you want to use the git version (or pre-releases, `pip install --pre python-miio`) until version 0.6.0 is released.**

## Getting started

The `miiocli` command allows controlling supported devices from the
command line, given that you know their IP addresses and tokens.

The simplest way to acquire the tokens is by using the `miiocli cloud` command,
which fetches them for you from your cloud account using [micloud](https://github.com/Squachen/micloud/):

    miiocli cloud
    Username: example@example.com
    Password:

    == name of the device (Device offline ) ==
        Model: example.device.v1
        Token: b1946ac92492d2347c6235b4d2611184
        IP: 192.168.xx.xx (mac: ab:cd:ef:12:34:56)
        DID: 123456789
        Locale: cn

Alternatively, [see the docs](https://python-miio.readthedocs.io/en/latest/discovery.html#obtaining-tokens)
for other ways to obtain them.

After you have your token, you can start controlling the device.
First, you can use `info` to get some generic information from any (even yet unsupported) device:

    miiocli device --ip <ip> --token <token> info

    Model: rockrobo.vacuum.v1
    Hardware version: MW300
    Firmware version: 1.2.4_16
    Supported using: RoborockVacuum
    Command: miiocli roborockvacuum --ip 127.0.0.1 --token 00000000000000000000000000000000
    Supported by genericmiot: True

Note that the command field which gives you the direct command to use for controlling the device.
If the device is supported by the `genericmiot` integration as stated in the output,
you can also use [`miiocli genericmiot` for controlling it](#controlling-modern-miot-devices).

You can always use `--help` to get more information about available
commands, subcommands, and their options.

## Controlling modern (MIoT) devices

Most modern (MIoT) devices are automatically supported by the `genericmiot` integration.
Internally, it uses (["miot spec"](https://home.miot-spec.com/)) files to find out about supported features,
such as sensors, settings and actions.

This device model specific file will be downloaded (and cached locally) when you use the `genericmiot` integration for the first time.

All features of supported devices are available using the common commands `status` (to show the device state), `set` (to change the settings), `actions` to list available actions and `call` to execute actions.

### Device status

Executing `status` will show the current device state, and also the accepted values for settings (marked with access `RW`):

    miiocli genericmiot --ip 127.0.0.1 --token 00000000000000000000000000000000 status

    Service Light (light)
            Switch Status (light:on, access: RW): False (<class 'bool'>, )
            Brightness (light:brightness, access: RW): 60 % (<class 'int'>, min: 1, max: 100, step: 1)
            Power Off Delay Time (light:off-delay-time, access: RW): 1:47:00 (<class 'int'>, min: 0, max: 120, step: 1)

### Changing settings

To change a setting, you need to provide the name of the setting (e.g., `light:brightness` in the example above):

     miiocli genericmiot --ip 127.0.0.1 --token 00000000000000000000000000000000 set light:brightness 0

     [{'did': 'light:brightness', 'siid': 2, 'piid': 3, 'code': 0}]

### Using actions

Most devices will also offer actions:

    miiocli genericmiot --ip 127.0.0.1 --token 00000000000000000000000000000000 actions

    Light (light)
            light:toggle            Toggle
            light:brightness-down   Brightness Down
            light:brightness-up     Brightness Up


These can be executed using the `call` command:

    miiocli genericmiot --ip 127.0.0.1 --token 00000000000000000000000000000000 call light:toggle

    {'code': 0, 'out': []}


Use `miiocli genericmiot --help` for more available commands.

**Note, using this integration requires you to use the git version until [version 0.6.0](https://github.com/rytilahti/python-miio/issues/1114) is released.**

## Controlling older (miIO) devices

Older devices are mainly supported by their corresponding modules (e.g.,
`roborockvacuum` or `fan`).
The `info` command will output the command to use, if the device is supported.

You can get the list of available commands for any given module by
passing `--help` argument to it:

    $ miiocli roborockvacuum --help

    Usage: miiocli roborockvacuum [OPTIONS] COMMAND [ARGS]...

    Options:
      --ip TEXT       [required]
      --token TEXT    [required]
      --id-file FILE
      --help          Show this message and exit.

    Commands:
      add_timer                Add a timer.
      ..

Each command invocation will automatically try to detect the device model.
In some situations (e.g., if the device has no cloud connectivity) this information
may not be available, causing an error.
Defining the model manually allows to skip the model detection:

    miiocli roborockvacuum --model roborock.vacuum.s5 --ip <ip> --token <token> start

## Troubleshooting

The `miiocli` tool has a `--debug` (`-d`) flag that can be used to enable debug logging.
You can repeat this multiple times (e.g., `-dd`) to increase the verbosity of the output.

You can find some solutions for the most common problems can be found in
[Troubleshooting](https://python-miio.readthedocs.io/en/latest/troubleshooting.html)
section.

If you have any questions, feel free to create an issue or start a discussion on GitHub.
Alternatively, you can check [our Matrix room](https://matrix.to/#/#python-miio-chat:matrix.org).


## API usage

All functionalities of this library are accessible through the `miio`
module. While you can initialize individual integration classes
manually, the simplest way to obtain a device instance is to use
`DeviceFactory`:

    from miio import DeviceFactory

    dev = DeviceFactory.create("<ip address>", "<token>")
    dev.status()

This will perform an `info` query to the device to detect the model,
and construct the corresponding device class for you.

### Introspecting supported features

You can introspect device classes using the following methods:

* `sensors()` to obtain information about sensors.
* `settings()` to obtain information about available settings that can be changed.
* `actions()` to return information about available device actions.

Each of these return [device descriptor
objects](https://python-miio.readthedocs.io/en/latest/api/miio.descriptors.html),
which contain the necessary metadata about the available features to
allow constructing generic interfaces.

**Note: some integrations may not have descriptors defined. [Adding them is straightforward](https://python-miio.readthedocs.io/en/latest/contributing.html#status-containers), so feel free to contribute!**

## Contributing

We welcome all sorts of contributions: from improvements
or fixing bugs to improving the documentation. We have prepared [a short
guide](https://python-miio.readthedocs.io/en/latest/contributing.html)
for getting you started.

## Simulators

If you are a developer working on a project that communicates using the miIO/MIoT protocol,
or want to contribute to this project but do not have a specific device,
you can use the simulators provided by this project.
The `miiocli` tool ships with [simple simulators for both miIO and MIoT](https://python-miio.readthedocs.io/en/latest/simulator.html) that can be used to test your code.

## Supported devices

While all MIoT devices are supported through the `genericmiot`
integration, this library supports also the following devices:

* Xiaomi Mi Robot Vacuum V1, S4, S4 MAX, S5, S5 MAX, S6 Pure, M1S, S7
* Xiaomi Mi Home Air Conditioner Companion
* Xiaomi Mi Smart Air Conditioner A (xiaomi.aircondition.mc1, mc2, mc4, mc5)
* Xiaomi Mi Air Purifier 2, 3H, 3C, 4, Pro, Pro H, 4 Pro (zhimi.airpurifier.m2, mb3, mb4, mb5, v7, vb2, va2), 4 Lite
* Xiaomi Mi Air (Purifier) Dog X3, X5, X7SM (airdog.airpurifier.x3, x5, x7sm)
* Xiaomi Mi Air Humidifier
* Smartmi Air Purifier
* Xiaomi Aqara Camera
* Xiaomi Aqara Gateway (basic implementation, alarm, lights)
* Xiaomi Mijia 360 1080p
* Xiaomi Mijia STYJ02YM (Viomi)
* Xiaomi Mijia 1C STYTJ01ZHM (Dreame)
* Dreame F9, D9, L10 Pro, Z10 Pro
* Dreame Trouver Finder
* Xiaomi Mi Home (Mijia) G1 Robot Vacuum Mop MJSTG1
* Xiaomi Roidmi Eve
* Xiaomi Mi Smart WiFi Socket
* Xiaomi Chuangmi camera (chuangmi.camera.ipc009, ipc013, ipc019, 038a2)
* Xiaomi Chuangmi Plug V1 (1 Socket, 1 USB Port)
* Xiaomi Chuangmi Plug V3 (1 Socket, 2 USB Ports)
* Xiaomi Smart Power Strip V1 and V2 (WiFi, 6 Ports)
* Xiaomi Philips Eyecare Smart Lamp 2
* Xiaomi Philips RW Read (philips.light.rwread)
* Xiaomi Philips LED Ceiling Lamp
* Xiaomi Philips LED Ball Lamp (philips.light.bulb)
* Xiaomi Philips LED Ball Lamp White (philips.light.hbulb)
* Xiaomi Philips Zhirui Smart LED Bulb E14 Candle Lamp
* Xiaomi Philips Zhirui Bedroom Smart Lamp
* Huayi Huizuo Lamps
* Xiaomi Universal IR Remote Controller (Chuangmi IR)
* Xiaomi Mi Smart Pedestal Fan V2, V3, SA1, ZA1, ZA3, ZA4, ZA5 1C, P5, P9, P10, P11, P15, P18, P33, P39, P45
* Xiaomi Rosou SS4 Ventilator (leshow.fan.ss4)
* Xiaomi Mi Air Humidifier V1, CA1, CA4, CB1, MJJSQ, JSQ, JSQ1, JSQ001
* Xiaomi Mi Water Purifier (Basic support: Turn on & off)
* Xiaomi Mi Water Purifier D1, C1 (Triple Setting)
* Xiaomi PM2.5 Air Quality Monitor V1, B1, S1
* Xiaomi Smart WiFi Speaker
* Xiaomi Mi WiFi Repeater 2
* Xiaomi Mi Smart Rice Cooker
* Xiaomi Smartmi Fresh Air System VA2 (zhimi.airfresh.va2), VA4 (va4), T2017 (t2017), A1 (dmaker.airfresh.a1)
* Yeelight lights (see also [python-yeelight](https://gitlab.com/stavros/python-yeelight/))
* Xiaomi Mi Air Dehumidifier
* Xiaomi Tinymu Smart Toilet Cover
* Xiaomi 16 Relays Module
* Xiaomi Xiao AI Smart Alarm Clock
* Smartmi Radiant Heater Smart Version (ZA1 version)
* Xiaomi Mi Smart Space Heater
* Xiaomiyoupin Curtain Controller (Wi-Fi) (lumi.curtain.hagl05)
* Xiaomi Dishwasher (viomi.dishwasher.m02)
* Xiaomi Xiaomi Mi Smart Space Heater S (zhimi.heater.mc2)
* Xiaomi Xiaomi Mi Smart Space Heater 1S (zhimi.heater.za2)
* Yeelight Dual Control Module (yeelink.switch.sw1)
* Scishare coffee maker (scishare.coffee.s1102)
* Qingping Air Monitor Lite (cgllc.airm.cgdn1)
* Xiaomi Walkingpad A1 (ksmb.walkingpad.v3)
* Xiaomi Smart Pet Water Dispenser (mmgg.pet_waterer.s1, s4, wi11)
* Xiaomi Mi Smart Humidifer S (jsqs, jsq5)
* Xiaomi Mi Robot Vacuum Mop 2 (Pro+, Ultra)

*Feel free to create a pull request to add support for new devices as
well as additional features for already supported ones.*

## Projects using this library

If you are using this library for your project, feel free to open a PR
to get it listed here!

### Home Assistant (official)

Home Assistant uses this library to support several platforms
out-of-the-box. This list is incomplete as the platforms (in
parentheses) may also support other devices listed above.

* [Xiaomi Mi Robot Vacuum](https://home-assistant.io/components/vacuum.xiaomi_miio/) (vacuum)
* [Xiaomi Philips Light](https://home-assistant.io/components/light.xiaomi_miio/) (light)
* [Xiaomi Mi Air Purifier and Air Humidifier](https://home-assistant.io/components/fan.xiaomi_miio/) (fan)
* [Xiaomi Smart WiFi Socket and Smart Power Strip](https://home-assistant.io/components/switch.xiaomi_miio/) (switch)
* [Xiaomi Universal IR Remote Controller](https://home-assistant.io/components/remote.xiaomi_miio/) (remote)
* [Xiaomi Mi Air Quality Monitor (PM2.5)](https://home-assistant.io/components/sensor.xiaomi_miio/) (sensor)
* [Xiaomi Aqara Gateway Alarm](https://home-assistant.io/components/alarm_control_panel.xiaomi_miio/) (alarm_control_panel)
* [Xiaomi Mi WiFi Repeater 2](https://www.home-assistant.io/components/device_tracker.xiaomi_miio/) (device_tracker)

### Home Assistant (custom)

* [Xiaomi Mi Home Air Conditioner Companion](https://github.com/syssi/xiaomi_airconditioningcompanion)
* [Xiaomi Mi Smart Pedestal Fan](https://github.com/syssi/xiaomi_fan)
* [Xiaomi Mi Smart Rice Cooker](https://github.com/syssi/xiaomi_cooker)
* [Xiaomi Raw Sensor](https://github.com/syssi/xiaomi_raw)
* [Xiaomi MIoT Devices](https://github.com/ha0y/xiaomi_miot_raw)
* [Xiaomi Miot Auto](https://github.com/al-one/hass-xiaomi-miot)

## Other related projects

This is a list of other projects around the Xiaomi ecosystem that you
can find interesting. Feel free to submit more related projects.

* [dustcloud](https://github.com/dgiese/dustcloud) (reverse engineering and rooting xiaomi devices)
* [Valetudo](https://github.com/Hypfer/Valetudo) (cloud free vacuum firmware)
* [micloud](https://github.com/Squachen/micloud) (library to access xiaomi cloud services, can be used to obtain device tokens)
* [micloudfaker](https://github.com/unrelentingtech/micloudfaker) (dummy cloud server, can be used to fix powerstrip status requests when without internet access)
* [Xiaomi Cloud Tokens Extractor](https://github.com/PiotrMachowski/Xiaomi-cloud-tokens-extractor) (an alternative way to fetch tokens from the cloud)
* [Your project here? Feel free to open a PR!](https://github.com/rytilahti/python-miio/pulls)
