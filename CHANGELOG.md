# Change Log

## [0.3.7](https://github.com/rytilahti/python-miio/tree/0.3.7)

This is a bugfix release which provides improved stability and compatibility.

[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.3.6...0.3.7)

**Closed issues:**

- construct.core.StreamError: could not write bytes, expected 4, found 8 [\#227](https://github.com/rytilahti/python-miio/issues/227)
- yeelink.light.color1 unsupported [\#225](https://github.com/rytilahti/python-miio/issues/225)
- Cant decode token \(invalid start byte\) [\#224](https://github.com/rytilahti/python-miio/issues/224)
- from Construct developer, a note [\#222](https://github.com/rytilahti/python-miio/issues/222)

**Merged pull requests:**

- Proper handling of the device\_id representation [\#228](https://github.com/rytilahti/python-miio/pull/228) ([syssi](https://github.com/syssi))
- Construct related, support upto 2.9.31 [\#226](https://github.com/rytilahti/python-miio/pull/226) ([arekbulski](https://github.com/arekbulski))

## [0.3.6](https://github.com/rytilahti/python-miio/tree/0.3.6)

This is a bugfix release because of further breaking changes of the underlying library construct.

Improvements:
* Lazy discovery on demand (@syssi)
* Support of construct 2.9.23 to 2.9.30 (@yawor, @syssi)
* Avoid device crash on wrap around of the sequence number (@syssi)
* Extended support of the Philips Ceiling Lamp (@syssi)

[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.3.5...0.3.6)

**Closed issues:**

- Unable to discover a device [\#217](https://github.com/rytilahti/python-miio/issues/217)
- AirPurifier set\_mode [\#213](https://github.com/rytilahti/python-miio/issues/213)
- Construct 2.9.28 breaks the Chuangmi IR packet assembly [\#212](https://github.com/rytilahti/python-miio/issues/212)
- Set mode for Air Purifier 2 not working [\#207](https://github.com/rytilahti/python-miio/issues/207)
- Trying to get map data without rooting [\#206](https://github.com/rytilahti/python-miio/issues/206)
- Unknown miio device found [\#204](https://github.com/rytilahti/python-miio/issues/204)
- Supporting raw and pronto optional parameter without type specifier. [\#199](https://github.com/rytilahti/python-miio/issues/199)

**Merged pull requests:**

- Fixes for the API change of construct v2.9.30 [\#220](https://github.com/rytilahti/python-miio/pull/220) ([syssi](https://github.com/syssi))
- Philips Ceiling Lamp: New setter "bricct" added [\#216](https://github.com/rytilahti/python-miio/pull/216) ([syssi](https://github.com/syssi))
- Lazy discovery on demand [\#215](https://github.com/rytilahti/python-miio/pull/215) ([syssi](https://github.com/syssi))
- Chuangmi IR: Fix Construct 2.9.28 regression [\#214](https://github.com/rytilahti/python-miio/pull/214) ([yawor](https://github.com/yawor))
- Philips Bulb crashs if \_id is 0 [\#211](https://github.com/rytilahti/python-miio/pull/211) ([syssi](https://github.com/syssi))

## [0.3.5](https://github.com/rytilahti/python-miio/tree/0.3.5)

This release provides major improvements for various supported devices. Special thanks goes to @yawor for his awesome work!

Additionally, a compatibility issue when using construct version 2.9.23 and greater -- causing timeouts and inability to control devices -- has been fixed again.

Device errors are now wrapped in a exception (DeviceException) for easier handling.

New devices:
* Air Purifier: Some additional models added to the list of supported and discovered devices by mDNS (@syssi)
* Air Humidifier CA added to the list of supported and discovered devices by mDNS (@syssi)

Improvements:
* Air Conditioning Companion: Extended device support (@syssi)
* Air Humidifier: Device support tested and improved (@syssi)
* Air Purifier Pro: Second motor speed and filter type detection added (@yawor)
* Air Purifier: Some additional properties added (@syssi)
* Air Quality Monitor: Additional property "time_state" added (@syssi)
* Revise error handling to be more consistent for library users (@rytilahti)
* Chuangmi IR: Ability to send any Pronto Hex encoded IR command added (@yawor)
* Chuangmi IR: Command type autodetection added (@yawor)
* Philips Bulb: New command "bricct" added (@syssi)
* Command line interface: Make discovery to work with no IP addr and token, courtesy of @M0ses (@rytilahti)

[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.3.4...0.3.5)

**Fixed bugs:**

- TypeError: build\(\) takes 2 positional arguments but 3 were given [\#201](https://github.com/rytilahti/python-miio/issues/201)
- Error on build message [\#197](https://github.com/rytilahti/python-miio/issues/197)

**Closed issues:**

- Control Air purifier and Humidifier? [\#177](https://github.com/rytilahti/python-miio/issues/177)
- Construct error, "subcon should be a Construct field" [\#167](https://github.com/rytilahti/python-miio/issues/167)

**Merged pull requests:**

- mDNS discovery: Additional air humidifier model \(zhimi-humidifier-ca1\) added [\#200](https://github.com/rytilahti/python-miio/pull/200) ([syssi](https://github.com/syssi))
- Make discovery to work with no IP addr and token, courtesy of M0ses [\#198](https://github.com/rytilahti/python-miio/pull/198) ([rytilahti](https://github.com/rytilahti))
- Minimum supported version of construct specified [\#196](https://github.com/rytilahti/python-miio/pull/196) ([syssi](https://github.com/syssi))
- Chuangmi IR command type autodetection [\#195](https://github.com/rytilahti/python-miio/pull/195) ([yawor](https://github.com/yawor))
- Point hound-ci to the flake8 configuration. Second try. [\#193](https://github.com/rytilahti/python-miio/pull/193) ([syssi](https://github.com/syssi))
- Fix a breaking change of construct 2.9.23 [\#192](https://github.com/rytilahti/python-miio/pull/192) ([syssi](https://github.com/syssi))
- Air Purifier: SleepMode enum added. SleepMode isn't a subset of OperationMode [\#190](https://github.com/rytilahti/python-miio/pull/190) ([syssi](https://github.com/syssi))
- Point hound-ci to the flake8 configuration [\#189](https://github.com/rytilahti/python-miio/pull/189) ([syssi](https://github.com/syssi))
- Features of mixed air purifier models added [\#188](https://github.com/rytilahti/python-miio/pull/188) ([syssi](https://github.com/syssi))
- Air Quality Monitor: New property "time\_state" added [\#187](https://github.com/rytilahti/python-miio/pull/187) ([syssi](https://github.com/syssi))
- Philips Bulb: New setter "bricct" added [\#186](https://github.com/rytilahti/python-miio/pull/186) ([syssi](https://github.com/syssi))
- Tests for the Chuangmi IR controller [\#184](https://github.com/rytilahti/python-miio/pull/184) ([syssi](https://github.com/syssi))
- Chuangmi IR: Add ability to send any Pronto Hex encoded IR command. [\#183](https://github.com/rytilahti/python-miio/pull/183) ([yawor](https://github.com/yawor))
- Tests for the Xiaomi Air Conditioning Companion [\#182](https://github.com/rytilahti/python-miio/pull/182) ([syssi](https://github.com/syssi))
- Flake8 configuration updated [\#181](https://github.com/rytilahti/python-miio/pull/181) ([syssi](https://github.com/syssi))
- Revise error handling to be more consistent for library users [\#180](https://github.com/rytilahti/python-miio/pull/180) ([rytilahti](https://github.com/rytilahti))
- All device specific exceptions should derive from DeviceException [\#179](https://github.com/rytilahti/python-miio/pull/179) ([syssi](https://github.com/syssi))
- Air Purifier Pro second motor speed [\#176](https://github.com/rytilahti/python-miio/pull/176) ([yawor](https://github.com/yawor))
- Tests of the Air Purifier improved [\#174](https://github.com/rytilahti/python-miio/pull/174) ([syssi](https://github.com/syssi))
- New properties of the Xiaomi Air Humidifier added [\#173](https://github.com/rytilahti/python-miio/pull/173) ([syssi](https://github.com/syssi))
- Return type of the property "volume" should be Optional [\#172](https://github.com/rytilahti/python-miio/pull/172) ([syssi](https://github.com/syssi))
- Missing dependency "appdirs" added [\#171](https://github.com/rytilahti/python-miio/pull/171) ([syssi](https://github.com/syssi))
- Xiaomi Air Humidifier: Unavailable property "led" removed. [\#170](https://github.com/rytilahti/python-miio/pull/170) ([syssi](https://github.com/syssi))
- Extended Air Conditioning Companion support [\#169](https://github.com/rytilahti/python-miio/pull/169) ([syssi](https://github.com/syssi))

## [0.3.4](https://github.com/rytilahti/python-miio/tree/0.3.4)

The most significant change for this release is unbreaking the communication when using a recent versions of construct library (thanks to @syssi).
On top of that there are various smaller fixes and improvements, e.g. support for sound packs and running python-miio on Windows.

New devices:
* Air Purifier 2S added to the list of supported and discovered devices by mDNS (@harnash)

Improvements:
* Air Purifier Pro: support for sound volume level and illuminance sensor (@yawor)
* Vacuum: added sound pack handling and ability to change the sound volume (@rytilahti)
* Vacuum: better support for status information on the 2nd gen model (@hastarin)

[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.3.3...0.3.4)

**Fixed bugs:**

- Error with info command [\#156](https://github.com/rytilahti/python-miio/issues/156)
- Change hard coded /tmp to cross-platform tempfile [\#148](https://github.com/rytilahti/python-miio/issues/148)

**Closed issues:**

- mirobo vacuum sound volume control [\#159](https://github.com/rytilahti/python-miio/issues/159)
- wifi signal strength [\#155](https://github.com/rytilahti/python-miio/issues/155)
- xiaomi philips bulb & philips ceiling [\#151](https://github.com/rytilahti/python-miio/issues/151)
- Vaccum Timer / Timezone issue [\#149](https://github.com/rytilahti/python-miio/issues/149)
- Exception when displaying Power load using Plug CLI [\#144](https://github.com/rytilahti/python-miio/issues/144)
- Missing states and error\_codes [\#57](https://github.com/rytilahti/python-miio/issues/57)

**Merged pull requests:**

- Use appdirs' user\_cache\_dir for sequence file [\#165](https://github.com/rytilahti/python-miio/pull/165) ([rytilahti](https://github.com/rytilahti))
- Add a more helpful error message when info\(\) fails with an empty payload [\#164](https://github.com/rytilahti/python-miio/pull/164) ([rytilahti](https://github.com/rytilahti))
- Adding "Go to target" state description for Roborock S50. [\#163](https://github.com/rytilahti/python-miio/pull/163) ([hastarin](https://github.com/hastarin))
- Add ability to change the volume [\#162](https://github.com/rytilahti/python-miio/pull/162) ([rytilahti](https://github.com/rytilahti))
- Added Air Purifier 2S to supported devices [\#161](https://github.com/rytilahti/python-miio/pull/161) ([harnash](https://github.com/harnash))
- Modified to support zoned cleaning mode of Roborock S50. [\#160](https://github.com/rytilahti/python-miio/pull/160) ([hastarin](https://github.com/hastarin))
- Fix for a breaking change of construct 2.8.22 [\#158](https://github.com/rytilahti/python-miio/pull/158) ([syssi](https://github.com/syssi))
- Air Purifier Pro: support for sound volume level and fix for bright propery [\#157](https://github.com/rytilahti/python-miio/pull/157) ([yawor](https://github.com/yawor))
- Add preliminary support for managing sound files [\#154](https://github.com/rytilahti/python-miio/pull/154) ([rytilahti](https://github.com/rytilahti))

## [0.3.3](https://github.com/rytilahti/python-miio/tree/0.3.3)

This release brings support for Air Conditioner Companion along some improvements and an increase in the test coverage for future-proofing the code-base. Special thanks for this release goes to @syssi & to all new contributors!

A bug exposed in python-miio when using version 2.8.17 or newer of the underlying construct library -- causing timeouts and inability to control devices -- has also been fixed in this release.

New supported devices:
* Xiaomi Mi Home Air Conditioner Companion

Improvements:
* Mi Vacuum 2nd generation is now detected by discovery
* Air Purifier 2: expose additional properties
* Yeelight: parse RGB properly

[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.3.2...0.3.3)

**Implemented enhancements:**

- Xiaomi Mi Home Air Conditioner Companion support [\#76](https://github.com/rytilahti/python-miio/issues/76)

**Closed issues:**

- Philip Eye Care Lamp Got error when receiving: timed out [\#146](https://github.com/rytilahti/python-miio/issues/146)
- Can't reach my mirobo [\#145](https://github.com/rytilahti/python-miio/issues/145)
- installiation problems [\#130](https://github.com/rytilahti/python-miio/issues/130)
- Unable to discover Xiaomi Philips LED Bulb  [\#106](https://github.com/rytilahti/python-miio/issues/106)
- Xiaomi Mi Robot Vacuum 2nd support [\#90](https://github.com/rytilahti/python-miio/issues/90)

**Merged pull requests:**

- Update for Rock Robot \(Mi Robot gen 2\) [\#143](https://github.com/rytilahti/python-miio/pull/143) ([fanthos](https://github.com/fanthos))
- Unbreak the communication when using construct v2.8.17 [\#142](https://github.com/rytilahti/python-miio/pull/142) ([rytilahti](https://github.com/rytilahti))
- fix powerstate invalid [\#139](https://github.com/rytilahti/python-miio/pull/139) ([roiff](https://github.com/roiff))
- Unit tests for the Chuang Mi Plug V1 [\#137](https://github.com/rytilahti/python-miio/pull/137) ([syssi](https://github.com/syssi))
- Unit tests of the Xiaomi Power Strip extended [\#136](https://github.com/rytilahti/python-miio/pull/136) ([syssi](https://github.com/syssi))
- Unit tests for the Xiaomi Air Quality Monitor [\#135](https://github.com/rytilahti/python-miio/pull/135) ([syssi](https://github.com/syssi))
- Unit tests for the Xiaomi Air Humidifier [\#134](https://github.com/rytilahti/python-miio/pull/134) ([syssi](https://github.com/syssi))
- Unit tests for philips lights [\#133](https://github.com/rytilahti/python-miio/pull/133) ([syssi](https://github.com/syssi))
- Additional properties of the Xiaomi Air Purifier 2 introduced [\#132](https://github.com/rytilahti/python-miio/pull/132) ([syssi](https://github.com/syssi))
- Fix Yeelight RGB parsing [\#131](https://github.com/rytilahti/python-miio/pull/131) ([Sduniii](https://github.com/Sduniii))
- Xiaomi Air Conditioner Companion support [\#129](https://github.com/rytilahti/python-miio/pull/129) ([syssi](https://github.com/syssi))
- Fix manual\_control error message typo [\#127](https://github.com/rytilahti/python-miio/pull/127) ([skorokithakis](https://github.com/skorokithakis))
- bump to 0.3.2, add RELEASING.md for describing the process [\#126](https://github.com/rytilahti/python-miio/pull/126) ([rytilahti](https://github.com/rytilahti))

## [0.3.2](https://github.com/rytilahti/python-miio/tree/0.3.2)

This release includes small improvements for powerstrip and vacuum support.
Furthermore this is the first release with proper documentation.
Generated docs are available at https://python-miio.readthedocs.io - patches to improve them are more than welcome!

Improvements:
* Powerstrip: expose correct load power, works also now without cloud connectivity
* Vacuum: added ability to reset consumable states
* Vacuum: exposes time left before next sensor clean-up

[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.3.1...0.3.2)

**Closed issues:**

- philips.light.ceiling Unsupported device found! [\#118](https://github.com/rytilahti/python-miio/issues/118)
- Xiaomi Philips ceiling light automation [\#116](https://github.com/rytilahti/python-miio/issues/116)
- Unsupported device found [\#112](https://github.com/rytilahti/python-miio/issues/112)
- PM2.5 Faster Readout [\#111](https://github.com/rytilahti/python-miio/issues/111)

**Merged pull requests:**

- add pure text LICENSE [\#125](https://github.com/rytilahti/python-miio/pull/125) ([rytilahti](https://github.com/rytilahti))
- Add GPLv3 license [\#124](https://github.com/rytilahti/python-miio/pull/124) ([pluehne](https://github.com/pluehne))
- Don’t require typing with Python 3.5 and newer [\#123](https://github.com/rytilahti/python-miio/pull/123) ([pluehne](https://github.com/pluehne))
- Powerstrip fixes [\#121](https://github.com/rytilahti/python-miio/pull/121) ([rytilahti](https://github.com/rytilahti))
- Added time left for recommended sensor cleaning [\#119](https://github.com/rytilahti/python-miio/pull/119) ([bbbenji](https://github.com/bbbenji))
- Load power of the PowerStrip fixed and removed from the Plug [\#117](https://github.com/rytilahti/python-miio/pull/117) ([syssi](https://github.com/syssi))
- Reset consumable by name [\#115](https://github.com/rytilahti/python-miio/pull/115) ([mrin](https://github.com/mrin))
- Model name of the Xiaomi Philips Ceiling Lamp updated [\#113](https://github.com/rytilahti/python-miio/pull/113) ([syssi](https://github.com/syssi))
- Update apidocs for sphinx-generated documentation, which follows at l… [\#93](https://github.com/rytilahti/python-miio/pull/93) ([rytilahti](https://github.com/rytilahti))

## [0.3.1](https://github.com/rytilahti/python-miio/tree/0.3.1) (2017-11-01)

New supported devices:
* Xioami Philips Smart LED Ball Lamp

Improvements:
* Vacuum: add ability to configure used wifi network
* Plug V1: improved discovery, add temperature reporting
* Airpurifier: setting of favorite level works now
* Eyecare: safer mapping of properties

Breaking:
* Strip has been renamed to PowerStrip to avoid confusion

[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.3.0...0.3.1)

**Fixed bugs:**

- AirPurifier: set\_favorite\_level not working [\#103](https://github.com/rytilahti/python-miio/issues/103)

**Closed issues:**

- Unsupported device [\#108](https://github.com/rytilahti/python-miio/issues/108)
- Xiaomi Vacuum resume cleaning session from dock capability? [\#102](https://github.com/rytilahti/python-miio/issues/102)

**Merged pull requests:**

- Chuang Mi Plug V1: Property "temperature" added & discovery fixed [\#109](https://github.com/rytilahti/python-miio/pull/109) ([syssi](https://github.com/syssi))
- Add the ability to define a timezone for configure\_wifi [\#107](https://github.com/rytilahti/python-miio/pull/107) ([rytilahti](https://github.com/rytilahti))
- Make vacuum robot wifi settings configurable via CLI [\#105](https://github.com/rytilahti/python-miio/pull/105) ([infinitydev](https://github.com/infinitydev))
- API call set\_favorite\_level \(method: set\_level\_favorite\) updated [\#104](https://github.com/rytilahti/python-miio/pull/104) ([syssi](https://github.com/syssi))
- use upstream android\_backup [\#101](https://github.com/rytilahti/python-miio/pull/101) ([rytilahti](https://github.com/rytilahti))
- add some tests to vacuum [\#100](https://github.com/rytilahti/python-miio/pull/100) ([rytilahti](https://github.com/rytilahti))
- Add a base to allow easier testing of devices [\#99](https://github.com/rytilahti/python-miio/pull/99) ([rytilahti](https://github.com/rytilahti))
- Rename of Strip to PowerStrip to avoid confusion with led strips [\#97](https://github.com/rytilahti/python-miio/pull/97) ([syssi](https://github.com/syssi))
- Some typing hints added and the code order aligned [\#96](https://github.com/rytilahti/python-miio/pull/96) ([syssi](https://github.com/syssi))
- Philips Eyecare: More safety property mapping of the device status [\#95](https://github.com/rytilahti/python-miio/pull/95) ([syssi](https://github.com/syssi))
- Device support of the Xioami Philips Smart LED Ball Lamp [\#94](https://github.com/rytilahti/python-miio/pull/94) ([syssi](https://github.com/syssi))

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
