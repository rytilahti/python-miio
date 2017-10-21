# Change Log

## [0.3.0](https://github.com/rytilahti/python-miio/tree/0.3.0) (2017-10-21)
Good bye to python-mirobo, say hello to python-miio!
As the library is getting more mature and supports so many other devices besides the vacuum sporting the miIO protocol,
it was decided that the project deserves a new name.
The name python-miio was previously used by a fork of python-mirobo, and we are thankful to SchumyHao for releasing the name for us.

The old "mirobo" package will continue working (and is API compatible) for the foreseeable future,
however, developers using this package (if any) are encouraged to port their code over to use the the new "miio" package.
The old command-line tools remain as they are.

In order to simplify the initial configuration, a tool to extract tokens from a Mi Home's backup (Android) or its database (Apple, Android) is added. It will also decrypt the tokens if needed, a change which was introduced recently how they are stored in the database of iOS devices.

Improvements:
* Vacuum: add support for configuring scheduled cleaning
* Vacuum: more user-friendly do-not-disturb reporting
* Vacuum: VacuumState's 'dnd' and 'in_cleaning' properties are deprecated in favor of 'dnd_status' and 'is_on'.
* Power Strip: load power is returned now correctly
* Yeelight: allow configuring 'developer mode', 'save state on change', and internal name
* Properties common for several devices are now named more consistently

New supported devices:
* Xiaomi PM2.5 Air Quality Monitor
* Xiaomi Water Purifier
* Xiaomi Air Humidifier
* Xiaomi Smart Wifi Speaker (incomplete, help wanted)
    
[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.2.0...0.3.0)

**Implemented enhancements:**

- Column ZToken of the iOS app contains a 96 character token [\#75](https://github.com/rytilahti/python-miio/issues/75)
- Xiaomi PM2.5 Air Quality Monitor support [\#70](https://github.com/rytilahti/python-miio/issues/70)

**Closed issues:**

- Calling message handler 'onHeartbeat'. [\#82](https://github.com/rytilahti/python-miio/issues/82)
- How do I find more features? [\#10](https://github.com/rytilahti/python-miio/issues/10)

**Merged pull requests:**

- Device support of the Xiaomi PM2.5 Air Quality Monitor introduced [\#89](https://github.com/rytilahti/python-miio/pull/89) ([syssi](https://github.com/syssi))
- wrap vacuum's dnd status inside an object [\#87](https://github.com/rytilahti/python-miio/pull/87) ([rytilahti](https://github.com/rytilahti))
- Initial support for wifi speakers [\#86](https://github.com/rytilahti/python-miio/pull/86) ([rytilahti](https://github.com/rytilahti))
- Extend yeelight support [\#85](https://github.com/rytilahti/python-miio/pull/85) ([rytilahti](https://github.com/rytilahti))
- Discovery: Device name of the zimi powerstrip v2 fixed [\#84](https://github.com/rytilahti/python-miio/pull/84) ([syssi](https://github.com/syssi))
- Rename the project to python-miio [\#83](https://github.com/rytilahti/python-miio/pull/83) ([rytilahti](https://github.com/rytilahti))
- Device support of the Xiaomi Power Strip updated [\#81](https://github.com/rytilahti/python-miio/pull/81) ([syssi](https://github.com/syssi))
- WIP: Extract Android backups, yield devices instead of just echoing [\#80](https://github.com/rytilahti/python-miio/pull/80) ([rytilahti](https://github.com/rytilahti))
- add a note about miio-extract-tokens [\#79](https://github.com/rytilahti/python-miio/pull/79) ([rytilahti](https://github.com/rytilahti))
- Implement adding, deleting and updating the timer [\#78](https://github.com/rytilahti/python-miio/pull/78) ([rytilahti](https://github.com/rytilahti))
- Add miio-extract-tokens tool for extracting tokens from sqlite databases [\#77](https://github.com/rytilahti/python-miio/pull/77) ([rytilahti](https://github.com/rytilahti))
- WIP: Avoid discovery flooding [\#72](https://github.com/rytilahti/python-miio/pull/72) ([syssi](https://github.com/syssi))
- mDNS discovery: New air purifier model \(zhimi-airpurifier-m2\) [\#68](https://github.com/rytilahti/python-miio/pull/68) ([syssi](https://github.com/syssi))
- First draft of the water purifier support [\#67](https://github.com/rytilahti/python-miio/pull/67) ([syssi](https://github.com/syssi))
- Device support of the Xiaomi Air Humidifier [\#66](https://github.com/rytilahti/python-miio/pull/66) ([syssi](https://github.com/syssi))
- Device info extended by two additional properties [\#65](https://github.com/rytilahti/python-miio/pull/65) ([syssi](https://github.com/syssi))
- Abstract device model exteded by model name \(identifier\) [\#64](https://github.com/rytilahti/python-miio/pull/64) ([syssi](https://github.com/syssi))
- Adjust property names of some devices  [\#63](https://github.com/rytilahti/python-miio/pull/63) ([syssi](https://github.com/syssi))

## [0.2.0](https://github.com/rytilahti/python-miio/tree/0.2.0) (2017-09-05)

Considering how far this project has evolved from being just an interface for the Xiaomi vacuum, it is time to leave 0.1 series behind and call this 0.2.0.

This release brings support to a couple of new devices, and contains fixes for some already supported ones.
All thanks for the improvements in this release go to syssi!
    
* Extended mDNS discovery to support more devices (@syssi)
* Improved support for the following devices:
    * Air purifier (@syssi)
    * Philips ball / Ceiling lamp (@syssi)
    * Xiaomi Strip (@syssi)
* New supported devices:
    * Chuangmi IR Remote control (@syssi)
    * Xiaomi Mi Smart Fan (@syssi)


[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.1.4...0.2.0)

**Closed issues:**

- Error in new mirobo/protocol.py [\#54](https://github.com/rytilahti/python-miio/issues/54)
- Some element about Xiaomi Philips Bulb [\#43](https://github.com/rytilahti/python-miio/issues/43)
- Philips Bulb and ceiling how to get token ? [\#42](https://github.com/rytilahti/python-miio/issues/42)
- Add support for other devices using the same protocol [\#17](https://github.com/rytilahti/python-miio/issues/17)
- Allow sending discovery packets to static IP address [\#5](https://github.com/rytilahti/python-miio/issues/5)

**Merged pull requests:**

- trivial: fix typo in automatic discovery description. [\#61](https://github.com/rytilahti/python-miio/pull/61) ([haim0n](https://github.com/haim0n))
- Some typos fixed [\#60](https://github.com/rytilahti/python-miio/pull/60) ([syssi](https://github.com/syssi))
- Fixes an AttributeError: PlugStatus object has no attribute current [\#59](https://github.com/rytilahti/python-miio/pull/59) ([syssi](https://github.com/syssi))
- Fixes various lint issues [\#58](https://github.com/rytilahti/python-miio/pull/58) ([syssi](https://github.com/syssi))
- Air Purifier: Set favorite level fixed [\#55](https://github.com/rytilahti/python-miio/pull/55) ([syssi](https://github.com/syssi))
- mDNS name of the Chuangmi Infrared Controller [\#53](https://github.com/rytilahti/python-miio/pull/53) ([syssi](https://github.com/syssi))
- Device support for the Xiaomi Mi Smart Fan [\#52](https://github.com/rytilahti/python-miio/pull/52) ([syssi](https://github.com/syssi))
- mDNS device map extended [\#51](https://github.com/rytilahti/python-miio/pull/51) ([syssi](https://github.com/syssi))
- Power strip: Fixes calculation of the instantaneous current [\#50](https://github.com/rytilahti/python-miio/pull/50) ([syssi](https://github.com/syssi))
- Air purifier: defaultdict used for safety and transparency [\#49](https://github.com/rytilahti/python-miio/pull/49) ([syssi](https://github.com/syssi))
- Device support for the Chuangmi IR Remote Controller [\#46](https://github.com/rytilahti/python-miio/pull/46) ([syssi](https://github.com/syssi))
- Xiaomi Ceiling Lamp: Some refactoring and fault tolerance if a philips light ball is used [\#45](https://github.com/rytilahti/python-miio/pull/45) ([syssi](https://github.com/syssi))
- New dependency "zeroconf" added. It's used for discovery now. [\#44](https://github.com/rytilahti/python-miio/pull/44) ([syssi](https://github.com/syssi))
- Readme for firmware \>= 3.3.9\_003077 \(Vacuum robot\) [\#41](https://github.com/rytilahti/python-miio/pull/41) ([mthoretton](https://github.com/mthoretton))
- Some improvements of the air purifier support [\#40](https://github.com/rytilahti/python-miio/pull/40) ([syssi](https://github.com/syssi))

## [0.1.4](https://github.com/rytilahti/python-miio/tree/0.1.4) (2017-08-23)

Fix dependencies


[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.1.3...0.1.4)

## [0.1.3](https://github.com/rytilahti/python-miio/tree/0.1.3) (2017-08-22)

* New commands:
    * --version to print out library version
    * info to return information about a device (requires token to be set)
    * serial_number (vacuum only)
    * timezone (getting and setting the timezone, vacuum only)
    * sound (querying)

* Supports for the following new devices thanks to syssi and kuduka:
    * Xiaomi Smart Power Strip (WiFi, 6 Ports) (@syssi)
    * Xiaomi Mi Air Purifier 2 (@syssi)
    * Xiaomi Mi Smart Socket Plug (1 Socket, 1 USB Port) (@syssi)
    * Xiaomi Philips Eyecare Smart Lamp 2 (@kuduka)
    * Xiaomi Philips LED Ceiling Lamp (@kuduka)
    * Xiaomi Philips LED Ball Lamp (@kuduka)

* Discovery now uses mDNS instead of handshake protocol. Old behavior still available with `--handshake true`
    
[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.1.2...0.1.3)

**Closed issues:**

- After updating to new firmware - can [\#37](https://github.com/rytilahti/python-miio/issues/37)
- CLI tool demands an IP address always [\#36](https://github.com/rytilahti/python-miio/issues/36)
- Use of both app and script not possible?  [\#30](https://github.com/rytilahti/python-miio/issues/30)
- Moving from custom\_components to HA version not working [\#28](https://github.com/rytilahti/python-miio/issues/28)
- Xiaomi Robot new Device ID [\#27](https://github.com/rytilahti/python-miio/issues/27)

**Merged pull requests:**

- Supported devices added to README.md and version bumped [\#39](https://github.com/rytilahti/python-miio/pull/39) ([syssi](https://github.com/syssi))
- Fix Home Assistant link to doc, using new `vacuum` component [\#38](https://github.com/rytilahti/python-miio/pull/38) ([azogue](https://github.com/azogue))
- Added support for Xiaomi Philips LED Ceiling Lamp [\#35](https://github.com/rytilahti/python-miio/pull/35) ([kuduka](https://github.com/kuduka))
- Added support for Xiaomi Philips Eyecare Smart Lamp 2 [\#34](https://github.com/rytilahti/python-miio/pull/34) ([kuduka](https://github.com/kuduka))
- Device support for the chuangmi plug v1 added [\#33](https://github.com/rytilahti/python-miio/pull/33) ([syssi](https://github.com/syssi))
- Device support for the xiaomi power strip added. [\#32](https://github.com/rytilahti/python-miio/pull/32) ([syssi](https://github.com/syssi))
- Device support for the xiaomi air purifier added. [\#31](https://github.com/rytilahti/python-miio/pull/31) ([syssi](https://github.com/syssi))

## [0.1.2](https://github.com/rytilahti/python-miio/tree/0.1.2) (2017-07-22)

* Add support for Wifi plugs (thanks to syssi)
* Make communication more robust by retrying automatically on errors

[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.1.1...0.1.2)

**Closed issues:**

- Pause not working in remote control mode [\#26](https://github.com/rytilahti/python-miio/issues/26)
- geht error singe 0.1.0 [\#25](https://github.com/rytilahti/python-miio/issues/25)
- Check that given token has correct length [\#11](https://github.com/rytilahti/python-miio/issues/11)

**Merged pull requests:**

- Device support for the xiaomi smart wifi socket added [\#29](https://github.com/rytilahti/python-miio/pull/29) ([syssi](https://github.com/syssi))

## [0.1.1](https://github.com/rytilahti/python-miio/tree/0.1.1) (2017-07-10)

add 'typing' requirement for python <3.5

[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.1.0...0.1.1)

**Closed issues:**

- No module named 'typing' [\#24](https://github.com/rytilahti/python-miio/issues/24)

## [0.1.0](https://github.com/rytilahti/python-miio/tree/0.1.0) (2017-07-08)

[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.0.9...0.1.0)

**Closed issues:**

- Error: Invalid value for "--id-file" [\#23](https://github.com/rytilahti/python-miio/issues/23)
- error on execute mirobo discover [\#22](https://github.com/rytilahti/python-miio/issues/22)
- Only one command working  [\#21](https://github.com/rytilahti/python-miio/issues/21)
- Integration in home assistant [\#4](https://github.com/rytilahti/python-miio/issues/4)

## [0.0.9](https://github.com/rytilahti/python-miio/tree/0.0.9) (2017-07-06)

fixes communication with newer firmwares

[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.0.8...0.0.9)

**Closed issues:**

- Feature request: show cleaning map [\#20](https://github.com/rytilahti/python-miio/issues/20)
- Command "map" and "raw\_command" - what do they do? [\#19](https://github.com/rytilahti/python-miio/issues/19)
- mirobo "DND enabled: 0", after change to 1 [\#18](https://github.com/rytilahti/python-miio/issues/18)
- Xiaomi vaccum control from Raspberry pi + iPad Mi app at the same time - token: b'ffffffffffffffffffffffffffffffff' [\#16](https://github.com/rytilahti/python-miio/issues/16)
- Not working with newest firmware version 3.3.9\_003073 [\#14](https://github.com/rytilahti/python-miio/issues/14)

## [0.0.8](https://github.com/rytilahti/python-miio/tree/0.0.8) (2017-06-05)
[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.0.7...0.0.8)

**Closed issues:**

- WIFI Switch for HA [\#12](https://github.com/rytilahti/python-miio/issues/12)
- Bug when having multiple network interfaces \(discovery\) [\#9](https://github.com/rytilahti/python-miio/issues/9)
- Get token from android App [\#8](https://github.com/rytilahti/python-miio/issues/8)
- Hello Thank you ！ [\#7](https://github.com/rytilahti/python-miio/issues/7)
- WARNING:root:could not open file'/etc/apt/sources.list' [\#6](https://github.com/rytilahti/python-miio/issues/6)

## [0.0.7](https://github.com/rytilahti/python-miio/tree/0.0.7) (2017-04-14)

cleanup in preparation for homeassistant inclusion

[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.0.6...0.0.7)

## [0.0.6](https://github.com/rytilahti/python-miio/tree/0.0.6) (2017-04-14)

cli improvements, total cleaning stats, remaining time for consumables

[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.0.5...0.0.6)

**Closed issues:**

- some concern about the new version [\#3](https://github.com/rytilahti/python-miio/issues/3)
- can't find my robot [\#2](https://github.com/rytilahti/python-miio/issues/2)
- \[Error\] Timout when querying for status [\#1](https://github.com/rytilahti/python-miio/issues/1)

## [0.0.5](https://github.com/rytilahti/python-miio/tree/0.0.5) (2017-04-14)


\* *This Change Log was automatically generated by [github_changelog_generator](https://github.com/skywinder/Github-Changelog-Generator)*
