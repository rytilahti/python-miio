# Change Log

## [0.4.7](https://github.com/rytilahti/python-miio/tree/0.4.7)

This release adds support for the following new devices:

* Widetech WDH318EFW1 dehumidifier \(nwt.derh.wdh318efw1\)
* Xiaomi Xiao AI Smart Alarm Clock \(zimi.clock.myk01\)
* Xiaomi Air Quality Monitor 2gen \(cgllc.airmonitor.b1\)
* Xiaomi ZNCZ05CM EU Smart Socket \(chuangmi.plug.hmi206\)

Fixes & Enhancements:

* Air Humidifier: Parsing of the firmware version improved
* Add travis build for python 3.7
* Use black for source code formatting
* Require python \>=3.6

[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.4.6...0.4.7)

**Implemented enhancements:**

- Add support for WIDETECH WDH318EFW1 dehumidifier \(nwt.derh.wdh318efw1\) [\#534](https://github.com/rytilahti/python-miio/issues/534)
- Support for Xiaomi Xiao AI Smart Alarm Clock \(zimi.clock.myk01\) [\#505](https://github.com/rytilahti/python-miio/issues/505)
- Add support for the cgllc.airmonitor.b1 [\#562](https://github.com/rytilahti/python-miio/pull/562) ([fwestenberg](https://github.com/fwestenberg))

**Fixed bugs:**

- Air Humidifier [\#529](https://github.com/rytilahti/python-miio/issues/529)

**Closed issues:**

- mirobo updater -- No request was made [\#557](https://github.com/rytilahti/python-miio/issues/557)
- What‘s the plan to release 0.4.6? [\#553](https://github.com/rytilahti/python-miio/issues/553)
- does this support aqara water leak sensor? [\#551](https://github.com/rytilahti/python-miio/issues/551)
- Unsupported device chuangmi.plug.hmi206 [\#545](https://github.com/rytilahti/python-miio/issues/545)
- python-miio not compatible with Python \<=3.5.1 [\#494](https://github.com/rytilahti/python-miio/issues/494)
- Support for Xiaomi Air Quality Monitor 2gen [\#419](https://github.com/rytilahti/python-miio/issues/419)

**Merged pull requests:**

- Add travis build for python 3.7 [\#561](https://github.com/rytilahti/python-miio/pull/561) ([syssi](https://github.com/syssi))
- bump required python version to 3.6+ [\#560](https://github.com/rytilahti/python-miio/pull/560) ([rytilahti](https://github.com/rytilahti))
- Use black for source code formatting [\#559](https://github.com/rytilahti/python-miio/pull/559) ([rytilahti](https://github.com/rytilahti))
- Add initial support for Xiao AI Smart Alarm Clock \(zimi.clock.myk01\) [\#558](https://github.com/rytilahti/python-miio/pull/558) ([rytilahti](https://github.com/rytilahti))
- Improve firmware version parser of the Air Humidifier \(Closes: \#529\) [\#556](https://github.com/rytilahti/python-miio/pull/556) ([syssi](https://github.com/syssi))
- Bring cgllc.airmonitor.s1 into line [\#555](https://github.com/rytilahti/python-miio/pull/555) ([syssi](https://github.com/syssi))
- Add Xiaomi ZNCZ05CM EU Smart Socket \(chuangmi.plug.hmi206\) support [\#554](https://github.com/rytilahti/python-miio/pull/554) ([syssi](https://github.com/syssi))


## [0.4.6](https://github.com/rytilahti/python-miio/tree/0.4.6)

This release adds support for the following new devices:

* Xiaomi Air Quality Monitor S1 \(cgllc.airmonitor.s1\)
* Xiaomi Mi Dehumidifier V1 \(nwt.derh.wdh318efw1\)
* Xiaomi Mi Roborock M1S and Mi Robot S1
* Xiaomi Mijia 360 1080p camera \(chuangmi.camera.ipc009\)
* Xiaomi Mi Smart Fan \(zhimi.fan.za3, zhimi.fan.za4, dmaker.fan.p5\)
* Xiaomi Smartmi Pure Evaporative Air Humidifier \(zhimi.humidifier.cb1\)
* Xiaomi Tinymu Smart Toilet Cover
* Xiaomi 16 Relays Module

Fixes & Enhancements:

* Air Conditioning Companion: Add particular swing mode values of a chigo air conditioner
* Air Humidifier: Handle poweroff exception on set\_mode
* Chuangmi IR controller: Add indicator led support
* Chuangmi IR controller: Add discovery of the Xiaomi IR remote 2gen \(chuangmi.remote.h102a03\)
* Chuangmi Plug: Fix set\_wifi\_led cli command
* Vacuum: Add state 18 as "segment cleaning"
* Device: Add easily accessible properties to DeviceError exception
* Always import DeviceError exception
* Require click version \>=7
* Remove pretty\_cron and typing dependencies from requirements.txt

[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.4.5...0.4.6)

**Closed issues:**

- Roborock Vacuum Bin full [\#546](https://github.com/rytilahti/python-miio/issues/546)
- Add support for Xiao AI Smart Alarm Clock [\#538](https://github.com/rytilahti/python-miio/issues/538)
- rockrobo.vacuum.v1 Error: No response from the device [\#536](https://github.com/rytilahti/python-miio/issues/536)
- Assistance [\#532](https://github.com/rytilahti/python-miio/issues/532)
- Unsupported device found - roborock.vacuum.s5 [\#527](https://github.com/rytilahti/python-miio/issues/527)
- Discovery mode to chuangmi\_camera. [\#522](https://github.com/rytilahti/python-miio/issues/522)
- 新款小米1X电风扇不支持 [\#520](https://github.com/rytilahti/python-miio/issues/520)
- Add swing mode of a Chigo Air Conditioner [\#518](https://github.com/rytilahti/python-miio/issues/518)
- Discover not working with Mi AirHumidifier CA1  [\#514](https://github.com/rytilahti/python-miio/issues/514)
- Question about vacuum errors\_codes duration [\#511](https://github.com/rytilahti/python-miio/issues/511)
- Support device model dmaker.fan.p5 [\#510](https://github.com/rytilahti/python-miio/issues/510)
- Roborock S50: ERROR:miio.updater:No request was made.. [\#508](https://github.com/rytilahti/python-miio/issues/508)
- Roborock S50: losing connection with mirobo [\#507](https://github.com/rytilahti/python-miio/issues/507)
- Support for Xiaomi IR Remote \(chuangmi.remote.v2\) [\#506](https://github.com/rytilahti/python-miio/issues/506)
- Support for Humidifier new model: zhimi.humidifier.cb1 [\#492](https://github.com/rytilahti/python-miio/issues/492)
- impossible to get the last version \(0.4.5\) or even the 0.4.4 [\#489](https://github.com/rytilahti/python-miio/issues/489)
- Getting the token of Air Purifier Pro v7 [\#461](https://github.com/rytilahti/python-miio/issues/461)
- Moonlight sync with HA [\#452](https://github.com/rytilahti/python-miio/issues/452)
- Replace pretty-cron dependency with cron\_descriptor [\#423](https://github.com/rytilahti/python-miio/issues/423)

**Merged pull requests:**

- remove pretty\_cron and typing dependencies from requirements.txt [\#548](https://github.com/rytilahti/python-miio/pull/548) ([rytilahti](https://github.com/rytilahti))
- Add tinymu smart toiletlid [\#544](https://github.com/rytilahti/python-miio/pull/544) ([scp10011](https://github.com/scp10011))
- Add support for Air Quality Monitor S1 \(cgllc.airmonitor.s1\) [\#539](https://github.com/rytilahti/python-miio/pull/539) ([zhumuht](https://github.com/zhumuht))
- Add pwzn relay [\#537](https://github.com/rytilahti/python-miio/pull/537) ([SchumyHao](https://github.com/SchumyHao))
- add mi dehumidifier v1 \(nwt.derh.wdh318efw1\) [\#535](https://github.com/rytilahti/python-miio/pull/535) ([stkang](https://github.com/stkang))
- add mi robot s1 \(m1s\) to discovery [\#531](https://github.com/rytilahti/python-miio/pull/531) ([rytilahti](https://github.com/rytilahti))
- Add preliminary Roborock M1S / Mi Robot S1 support [\#526](https://github.com/rytilahti/python-miio/pull/526) ([syssi](https://github.com/syssi))
- Add state 18 as "segment cleaning" [\#525](https://github.com/rytilahti/python-miio/pull/525) ([syssi](https://github.com/syssi))
- Add particular swing mode values of a chigo air conditioner [\#519](https://github.com/rytilahti/python-miio/pull/519) ([syssi](https://github.com/syssi))
- Add chuangmi.camera.ipc009 support [\#516](https://github.com/rytilahti/python-miio/pull/516) ([impankratov](https://github.com/impankratov))
- Add zhimi.fan.za3 support [\#515](https://github.com/rytilahti/python-miio/pull/515) ([syssi](https://github.com/syssi))
- Add dmaker.fan.p5 support [\#513](https://github.com/rytilahti/python-miio/pull/513) ([syssi](https://github.com/syssi))
- Add zhimi.fan.za4 support [\#512](https://github.com/rytilahti/python-miio/pull/512) ([syssi](https://github.com/syssi))
- Require click version \>=7 [\#503](https://github.com/rytilahti/python-miio/pull/503) ([fvollmer](https://github.com/fvollmer))
- Add indicator led support of the chuangmi.remote.h102a03 and chuangmi.remote.v2 [\#500](https://github.com/rytilahti/python-miio/pull/500) ([syssi](https://github.com/syssi))
- Chuangmi Plug: Fix set\_wifi\_led cli command [\#499](https://github.com/rytilahti/python-miio/pull/499) ([syssi](https://github.com/syssi))
- Add discovery of the Xiaomi IR remote 2gen \(chuangmi.remote.h102a03\) [\#497](https://github.com/rytilahti/python-miio/pull/497) ([syssi](https://github.com/syssi))
- Air Humidifier: Handle poweroff exception on set\_mode [\#496](https://github.com/rytilahti/python-miio/pull/496) ([syssi](https://github.com/syssi))
- Add zhimi.humidifier.cb1 support [\#493](https://github.com/rytilahti/python-miio/pull/493) ([antylama](https://github.com/antylama))
- Add easily accessible properties to DeviceError exception [\#488](https://github.com/rytilahti/python-miio/pull/488) ([syssi](https://github.com/syssi))
- Always import DeviceError exception [\#487](https://github.com/rytilahti/python-miio/pull/487) ([syssi](https://github.com/syssi))


## [0.4.5](https://github.com/rytilahti/python-miio/tree/0.4.5)

This release adds support for the following new devices:

* Xiaomi Chuangmi Plug M3
* Xiaomi Chuangmi Plug HMI205
* Xiaomi Air Purifier Pro V7
* Xiaomi Air Quality Monitor 2gen
* Xiaomi Aqara Camera

Fixes & Enhancements:

* Handle "resp invalid json" error
* Drop pretty\_cron dependency
* Make android\_backup an optional dependency
* Docs: Add troubleshooting guide for cross-subnet communications
* Docs: Fix link in discovery.rst
* Docs: Sphinx config fix
* Docs: Token extraction for Apple users
* Docs: Add a troubleshooting entry for vacuum timeouts
* Docs: New method to obtain tokens
* miio-extract-tokens: Allow extraction from Yeelight app db
* miio-extract-tokens: Fix for devices without tokens

API changes:

* Air Conditioning Partner: Add swing mode 7 with unknown meaning
* Air Conditioning Partner: Extract the return value of the plug\_state request properly
* Air Conditioning Partner: Expose power\_socket property
* Air Conditioning Partner: Fix some conversion issues
* Air Humidifier: Add set\_led method
* Air Humidifier: Rename speed property to avoid a name clash at HA
* Air Humidifier CA1: Fix led brightness command
* Air Purifier: Add favorite level 17
* Moonlight: Align signature of set\_brightness\_and\_rgb
* Moonlight: Fix parameters of the set\_rgb api call
* Moonlight: Night mode support and additional scenes
* Vacuum: Add control for persistent maps, no-go zones and barriers
* Vacuum: Add resume\_zoned\_clean\(\) and resume\_or\_start\(\) helper
* Vacuum: Additional error descriptions
* Yeelight Bedside: Fix set\_name and set\_color\_temp

[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.4.4...0.4.5)

**Fixed bugs:**

- miio-extract-tokens raises a TypeError when running against extracted SQLite database [\#467](https://github.com/rytilahti/python-miio/issues/467)
- Do not crash on last\_clean\_details when no history available [\#457](https://github.com/rytilahti/python-miio/issues/457)
- install-sound command not working on Xiaowa vacuum \(roborock.vacuum.c1 v1.3.0\) [\#418](https://github.com/rytilahti/python-miio/issues/418)
- DeviceError code -30001 \(Resp Invalid JSON\) - Philips Bulb [\#205](https://github.com/rytilahti/python-miio/issues/205)

**Closed issues:**

- Issues adding roborock s50 vacuum to HA and controlling from mirobo [\#456](https://github.com/rytilahti/python-miio/issues/456)
- Support for chuangmi plug m3 [\#454](https://github.com/rytilahti/python-miio/issues/454)
- Xiaomi Phillips Smart LED Ball Lamp and API token for Home Assistant \(yaml\) [\#445](https://github.com/rytilahti/python-miio/issues/445)
- xiaomi ir control [\#444](https://github.com/rytilahti/python-miio/issues/444)
- Mirobo does not start on raspberry pi [\#442](https://github.com/rytilahti/python-miio/issues/442)
- Add mi band 3 watch to your library [\#441](https://github.com/rytilahti/python-miio/issues/441)
- Unsupported Device: chuangmi.plug.hmi205 [\#440](https://github.com/rytilahti/python-miio/issues/440)
- Air Purifier zhimi.airpurifier.m1 set\_mode isn't working [\#436](https://github.com/rytilahti/python-miio/issues/436)
- Can't make it work in a Domoticz plugin [\#433](https://github.com/rytilahti/python-miio/issues/433)
- chuangmi.plug.hmi205 unsupported device [\#427](https://github.com/rytilahti/python-miio/issues/427)
- Some devices not responding across subnets. [\#422](https://github.com/rytilahti/python-miio/issues/422)

**Merged pull requests:**

- Add missing error description [\#483](https://github.com/rytilahti/python-miio/pull/483) ([oncleben31](https://github.com/oncleben31))
- Enable the night mode \(scene 6\) by calling "go\_night" [\#481](https://github.com/rytilahti/python-miio/pull/481) ([syssi](https://github.com/syssi))
- Philips Moonlight: Support up to 6 fixed scenes [\#478](https://github.com/rytilahti/python-miio/pull/478) ([syssi](https://github.com/syssi))
- Remove duplicate paragraph about "Tokens from Mi Home logs" [\#477](https://github.com/rytilahti/python-miio/pull/477) ([syssi](https://github.com/syssi))
- Make android\_backup an optional dependency [\#476](https://github.com/rytilahti/python-miio/pull/476) ([rytilahti](https://github.com/rytilahti))
- Drop pretty\_cron dependency [\#475](https://github.com/rytilahti/python-miio/pull/475) ([rytilahti](https://github.com/rytilahti))
- Vacuum: add resume\_zoned\_clean\(\) and resume\_or\_start\(\) helper [\#473](https://github.com/rytilahti/python-miio/pull/473) ([rytilahti](https://github.com/rytilahti))
- Check for empty clean\_history instead of crashing on it [\#472](https://github.com/rytilahti/python-miio/pull/472) ([rytilahti](https://github.com/rytilahti))
- Fix miio-extract-tokens for devices without tokens [\#469](https://github.com/rytilahti/python-miio/pull/469) ([domibarton](https://github.com/domibarton))
- Rename speed property to avoid a name clash at HA [\#466](https://github.com/rytilahti/python-miio/pull/466) ([syssi](https://github.com/syssi))
- Corrected link in discovery.rst and Xiaomi Air Purifier Pro fix [\#465](https://github.com/rytilahti/python-miio/pull/465) ([swiergot](https://github.com/swiergot))
- New method to obtain tokens [\#464](https://github.com/rytilahti/python-miio/pull/464) ([swiergot](https://github.com/swiergot))
- Add a troubleshooting entry for vacuum timeouts [\#463](https://github.com/rytilahti/python-miio/pull/463) ([rytilahti](https://github.com/rytilahti))
- Extend miio-extract-tokens to allow extraction from yeelight app db [\#462](https://github.com/rytilahti/python-miio/pull/462) ([rytilahti](https://github.com/rytilahti))
- Docs for token extraction for Apple users [\#460](https://github.com/rytilahti/python-miio/pull/460) ([domibarton](https://github.com/domibarton))
- Add troubleshooting guide for cross-subnet communications [\#459](https://github.com/rytilahti/python-miio/pull/459) ([domibarton](https://github.com/domibarton))
- Sphinx config fix [\#458](https://github.com/rytilahti/python-miio/pull/458) ([domibarton](https://github.com/domibarton))
- Add Xiaomi Chuangmi Plug M3 support \(Closes: \#454\) [\#455](https://github.com/rytilahti/python-miio/pull/455) ([syssi](https://github.com/syssi))
- Add a "Reviewed by Hound" badge [\#453](https://github.com/rytilahti/python-miio/pull/453) ([salbertson](https://github.com/salbertson))
- Air Humidifier: Add set\_led method [\#451](https://github.com/rytilahti/python-miio/pull/451) ([syssi](https://github.com/syssi))
- Air Humidifier CA1: Fix led brightness command [\#450](https://github.com/rytilahti/python-miio/pull/450) ([syssi](https://github.com/syssi))
- Handle "resp invalid json" error \(Closes: \#205\) [\#449](https://github.com/rytilahti/python-miio/pull/449) ([syssi](https://github.com/syssi))
- Air Conditioning Partner: Extract the return value of the plug\_state request properly [\#448](https://github.com/rytilahti/python-miio/pull/448) ([syssi](https://github.com/syssi))
- Expose power\_socket property at AirConditioningCompanionStatus.\_\_repr\_\_\(\) [\#447](https://github.com/rytilahti/python-miio/pull/447) ([syssi](https://github.com/syssi))
- Air Conditioning Companion: Fix some conversion issues [\#446](https://github.com/rytilahti/python-miio/pull/446) ([syssi](https://github.com/syssi))
- Add support v7 version for Xiaomi AirPurifier PRO [\#443](https://github.com/rytilahti/python-miio/pull/443) ([quamilek](https://github.com/quamilek))
- Add control for persistent maps, no-go zones and barriers [\#438](https://github.com/rytilahti/python-miio/pull/438) ([rytilahti](https://github.com/rytilahti))
- Moonlight: Fix parameters of the set\_rgb api call [\#435](https://github.com/rytilahti/python-miio/pull/435) ([syssi](https://github.com/syssi))
- yeelight bedside: fix set\_name and set\_color\_temp [\#434](https://github.com/rytilahti/python-miio/pull/434) ([rytilahti](https://github.com/rytilahti))
- AC Partner: Add swing mode 7 with unknown meaning [\#431](https://github.com/rytilahti/python-miio/pull/431) ([syssi](https://github.com/syssi))
- Philips Moonlight: Align signature of set\_brightness\_and\_rgb [\#430](https://github.com/rytilahti/python-miio/pull/430) ([syssi](https://github.com/syssi))
- Add support for next generation of the Xiaomi Mi Smart Plug  [\#428](https://github.com/rytilahti/python-miio/pull/428) ([syssi](https://github.com/syssi))
- Add Xiaomi Air Quality Monitor 2gen \(cgllc.airmonitor.b1\) support [\#420](https://github.com/rytilahti/python-miio/pull/420) ([syssi](https://github.com/syssi))
- Add initial support for aqara camera \(lumi.camera.aq1\) [\#375](https://github.com/rytilahti/python-miio/pull/375) ([rytilahti](https://github.com/rytilahti))


## [0.4.4](https://github.com/rytilahti/python-miio/tree/0.4.4) (2018-12-03)

This release adds support for the following new devices:

* Air Purifier 2s
* Vacuums roborock.vacuum.e2 and roborock.vacuum.c1 (limited features, sound packs are known not to be working)

Fixes & Enhancements:

* AC Partner V3: Add socket support
* AC Parner & AirHumidifer: improved autodetection
* Cooker: fixed model confusion
* Vacuum: add last_clean_details() to directly access the information from latest cleaning
* Yeelight: RGB support
* Waterpurifier: improved support

API changes:
* Vacuum: returning a list for clean_details() is deprecated and to be removed in the future.
* Philips Moonlight: RGB values are expected and delivered as tuples instead of an integer

[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.4.3...0.4.4)

**Implemented enhancements:**

- Not working with Rockrobo Xiaowa \(roborock.vacuum.e2\) [\#364](https://github.com/rytilahti/python-miio/issues/364)
- Support for new vacuum model Xiaowa E20  [\#348](https://github.com/rytilahti/python-miio/issues/348)

**Fixed bugs:**

- No working with Xiaowa \(roborock.vacuum.c1 v1.3.0\) [\#370](https://github.com/rytilahti/python-miio/issues/370)
- Send multiple params broken result [\#73](https://github.com/rytilahti/python-miio/issues/73)

**Closed issues:**

- Add lumi.gateway.aqhm01 as unsuppported gateway [\#424](https://github.com/rytilahti/python-miio/issues/424)
- Unsupported device zhimi.airpurifier.mc1 [\#403](https://github.com/rytilahti/python-miio/issues/403)
- xiaomi repeater v1 [\#396](https://github.com/rytilahti/python-miio/issues/396)
- Control Air Conditioner Companion like Xiaomi Mi Smart WiFi Socket [\#337](https://github.com/rytilahti/python-miio/issues/337)

**Merged pull requests:**

- Improve discovery a specific device models [\#421](https://github.com/rytilahti/python-miio/pull/421) ([syssi](https://github.com/syssi))
- Fix PEP8 lint issue: unexpected spaces around keyword / parameter equals [\#416](https://github.com/rytilahti/python-miio/pull/416) ([syssi](https://github.com/syssi))
- AC Partner V3: Add socket support \(Closes \#337\) [\#415](https://github.com/rytilahti/python-miio/pull/415) ([syssi](https://github.com/syssi))
- Moonlight: Provide property rgb as tuple [\#414](https://github.com/rytilahti/python-miio/pull/414) ([syssi](https://github.com/syssi))
- fix last\_clean\_details to return the latest, not the oldest [\#413](https://github.com/rytilahti/python-miio/pull/413) ([rytilahti](https://github.com/rytilahti))
- generate docs for more modules [\#412](https://github.com/rytilahti/python-miio/pull/412) ([rytilahti](https://github.com/rytilahti))
- Use pause instead of stop for home command [\#411](https://github.com/rytilahti/python-miio/pull/411) ([rytilahti](https://github.com/rytilahti))
- Add .readthedocs.yml [\#410](https://github.com/rytilahti/python-miio/pull/410) ([rytilahti](https://github.com/rytilahti))
- Fix serial number reporting for some devices, add locale command [\#409](https://github.com/rytilahti/python-miio/pull/409) ([rytilahti](https://github.com/rytilahti))
- Force parameters to be an empty list if none is given [\#408](https://github.com/rytilahti/python-miio/pull/408) ([rytilahti](https://github.com/rytilahti))
- Cooker: Fix mixed model name [\#406](https://github.com/rytilahti/python-miio/pull/406) ([syssi](https://github.com/syssi))
- Waterpurifier: Divide properties into multiple requests \(Closes: \#73\) [\#405](https://github.com/rytilahti/python-miio/pull/405) ([syssi](https://github.com/syssi))
- Add Xiaomi Air Purifier 2s support [\#404](https://github.com/rytilahti/python-miio/pull/404) ([syssi](https://github.com/syssi))
- Fixed typo in log message [\#402](https://github.com/rytilahti/python-miio/pull/402) ([microraptor](https://github.com/microraptor))


## [0.4.3](https://github.com/rytilahti/python-miio/tree/0.4.3)

This is a bugfix release which provides improved compatibility.

[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.4.2...0.4.3)

**Closed issues:**

- unsupported device zhimi airmonitor v1 [\#393](https://github.com/rytilahti/python-miio/issues/393)
- Unsupported device found: chuangmi.ir.v2 [\#392](https://github.com/rytilahti/python-miio/issues/392)
- TypeError: not all arguments converted during string formatting [\#385](https://github.com/rytilahti/python-miio/issues/385)
- Status not worked for AirHumidifier CA1 [\#383](https://github.com/rytilahti/python-miio/issues/383)
- Xiaomi Rice Cooker Normal5: get\_prop only works if "all" properties are requested [\#380](https://github.com/rytilahti/python-miio/issues/380)
- python-construct-2.9.45 [\#374](https://github.com/rytilahti/python-miio/issues/374)

**Merged pull requests:**

- Update commands in manual [\#398](https://github.com/rytilahti/python-miio/pull/398) ([olskar](https://github.com/olskar))
- Add cli interface for yeelight devices [\#397](https://github.com/rytilahti/python-miio/pull/397) ([rytilahti](https://github.com/rytilahti))
- Add last\_clean\_details to return information from the last clean [\#395](https://github.com/rytilahti/python-miio/pull/395) ([rytilahti](https://github.com/rytilahti))
- Add discovery of the Xiaomi Air Quality Monitor \(PM2.5\) \(Closes: \#393\) [\#394](https://github.com/rytilahti/python-miio/pull/394) ([syssi](https://github.com/syssi))
- Add miiocli support for the Air Humidifier CA1 [\#391](https://github.com/rytilahti/python-miio/pull/391) ([syssi](https://github.com/syssi))
- Add property LED to the Xiaomi Air Fresh [\#390](https://github.com/rytilahti/python-miio/pull/390) ([syssi](https://github.com/syssi))
- Fix Cooker Normal5: get\_prop only works if "all" properties are requested \(Closes: \#380\) [\#389](https://github.com/rytilahti/python-miio/pull/389) ([syssi](https://github.com/syssi))
- Improve the support of the Air Humidifier CA1 \(Closes: \#383\) [\#388](https://github.com/rytilahti/python-miio/pull/388) ([syssi](https://github.com/syssi))


## [0.4.2](https://github.com/rytilahti/python-miio/tree/0.4.2)

This release removes the version pinning for "construct" library as its API has been stabilized and we don't want to force our downstreams for our version choices.
Another notable change is dropping the "mirobo" package which has been deprecated for a very long time, and everyone using it should have had converted to use "miio" already.
Furthermore the client tools work now with click's version 7+.

This release also changes the behavior of vacuum's `got_error` property to signal properly if an error has occured. The previous behavior was based on checking the state instead of the error number, which changed after an error to 'idle' after a short while.

[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.4.1...0.4.2)

**Fixed bugs:**

- Zoned cleanup start and stops imediately [\#355](https://github.com/rytilahti/python-miio/issues/355)

**Closed issues:**

- STATE not supported: Updating, state\_code: 14 [\#381](https://github.com/rytilahti/python-miio/issues/381)
- cant get it to work with xiaomi robot vacuum cleaner s50 [\#378](https://github.com/rytilahti/python-miio/issues/378)
- airfresh problem [\#377](https://github.com/rytilahti/python-miio/issues/377)
- get device token is 000000000000000000 [\#366](https://github.com/rytilahti/python-miio/issues/366)
- Rockrobo firmware 3.3.9\_003254 [\#358](https://github.com/rytilahti/python-miio/issues/358)
- No response from the device on Xiaomi Roborock v2 [\#349](https://github.com/rytilahti/python-miio/issues/349)
- Information : Xiaomi Aqara Smart Camera Hack [\#347](https://github.com/rytilahti/python-miio/issues/347)

**Merged pull requests:**

- Fix click7 compatibility [\#387](https://github.com/rytilahti/python-miio/pull/387) ([rytilahti](https://github.com/rytilahti))
- Expand documentation for token from Android backup [\#382](https://github.com/rytilahti/python-miio/pull/382) ([sgtio](https://github.com/sgtio))
- vacuum's got\_error: compare against error code, not against the state [\#379](https://github.com/rytilahti/python-miio/pull/379) ([rytilahti](https://github.com/rytilahti))
- Add tqdm to requirements list [\#369](https://github.com/rytilahti/python-miio/pull/369) ([pluehne](https://github.com/pluehne))
- Improve repr format [\#368](https://github.com/rytilahti/python-miio/pull/368) ([syssi](https://github.com/syssi))


## [0.4.1](https://github.com/rytilahti/python-miio/tree/0.4.1)

This release provides support for some new devices, improved support of existing devices and various fixes.

New devices:
* Xiaomi Mijia Smartmi Fresh Air System Wall-Mounted (@syssi)
* Xiaomi Philips Zhirui Bedside Lamp (@syssi)

Improvements:
* Vacuum: Support of multiple zones for app\_zoned\_cleaning added (@ciB89)
* Fan: SA1 and ZA1 support added as well as various fixes and improvements (@syssi)
* Chuangmi Plug V3: Measurement unit of the power consumption fixed (@syssi)
* Air Humidifier: Strong mode property added (@syssi)


[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.4.0...0.4.1)

**Closed issues:**

- Xiaomi Rice Cooker component not working [\#365](https://github.com/rytilahti/python-miio/issues/365)
- vacuum refuses to answer if the access to internet is blocked [\#353](https://github.com/rytilahti/python-miio/issues/353)
- Xiaomi Philips Zhirui Bedside Lamp [\#351](https://github.com/rytilahti/python-miio/issues/351)
- Unable to get Xiaomi miplug working on HA [\#350](https://github.com/rytilahti/python-miio/issues/350)
- Error codes [\#346](https://github.com/rytilahti/python-miio/issues/346)
- miiocli plug does not show the USB power status [\#344](https://github.com/rytilahti/python-miio/issues/344)
- could you pls add support to gateway's functions of security and light? [\#340](https://github.com/rytilahti/python-miio/issues/340)
- miplug discover throws exception [\#339](https://github.com/rytilahti/python-miio/issues/339)
- miioclio: raw\_command\(\) got an unexpected keyword argument 'parameters' [\#335](https://github.com/rytilahti/python-miio/issues/335)
- qmi.powerstrip.v1 no longer working on 0.40 [\#334](https://github.com/rytilahti/python-miio/issues/334)
- Starting the vacuum clean up after remote control [\#235](https://github.com/rytilahti/python-miio/issues/235)

**Merged pull requests:**

- Fan: Fix broken model names [\#363](https://github.com/rytilahti/python-miio/pull/363) ([syssi](https://github.com/syssi))
- Xiaomi Mi Smart Pedestal Fan: Add ZA1 \(zimi.fan.za1\) support [\#362](https://github.com/rytilahti/python-miio/pull/362) ([syssi](https://github.com/syssi))
- ignore cli and test files from test coverage to get correct coverage percentage [\#361](https://github.com/rytilahti/python-miio/pull/361) ([rytilahti](https://github.com/rytilahti))
- Add Xiaomi Airfresh VA2 support [\#360](https://github.com/rytilahti/python-miio/pull/360) ([syssi](https://github.com/syssi))
- Add basic Philips Moonlight support \(Closes: \#351\) [\#359](https://github.com/rytilahti/python-miio/pull/359) ([syssi](https://github.com/syssi))
- Xiaomi Mi Smart Pedestal Fan: Add SA1 \(zimi.fan.sa1\) support [\#354](https://github.com/rytilahti/python-miio/pull/354) ([syssi](https://github.com/syssi))
- Fix "miplug discover" method \(Closes: \#339\) [\#342](https://github.com/rytilahti/python-miio/pull/342) ([syssi](https://github.com/syssi))
- Fix ChuangmiPlugStatus repr format [\#341](https://github.com/rytilahti/python-miio/pull/341) ([syssi](https://github.com/syssi))
- Chuangmi Plug V3: Fix measurement unit \(W\) of the power consumption \(load\_power\) [\#338](https://github.com/rytilahti/python-miio/pull/338) ([syssi](https://github.com/syssi))
- miiocli: Fix raw\_command parameters \(Closes: \#335\) [\#336](https://github.com/rytilahti/python-miio/pull/336) ([syssi](https://github.com/syssi))
- Fan: Fix a KeyError if button\_pressed isn't available [\#333](https://github.com/rytilahti/python-miio/pull/333) ([syssi](https://github.com/syssi))
- Fan: Add test for the natural speed setter [\#332](https://github.com/rytilahti/python-miio/pull/332) ([syssi](https://github.com/syssi))
- Fan: Divide the retrieval of properties into multiple requests [\#331](https://github.com/rytilahti/python-miio/pull/331) ([syssi](https://github.com/syssi))
- Support of multiple zones for app\_zoned\_cleaning [\#311](https://github.com/rytilahti/python-miio/pull/311) ([ciB89](https://github.com/ciB89))
- Air Humidifier: Strong mode property added and docstrings updated [\#300](https://github.com/rytilahti/python-miio/pull/300) ([syssi](https://github.com/syssi))


## [0.4.0](https://github.com/rytilahti/python-miio/tree/0.4.0)

The highlight of this release is a crisp, unified and scalable command line interface called `miiocli` (thanks @yawor). Each supported device of this library is already integrated.

New devices:
* Xiaomi Mi Smart Electric Rice Cooker (@syssi)

Improvements:
* Unified and scalable command line interface (@yawor)
* Air Conditioning Companion: Support for captured infrared commands added (@syssi)
* Air Conditioning Companion: LED property fixed (@syssi)
* Air Quality Monitor: Night mode added (@syssi)
* Chuangi Plug V3 support fixed (@syssi)
* Pedestal Fan: Improved support of both versions
* Power Strip: Both versions are fully supported now (@syssi)
* Vacuum: New commands app\_goto\_target and app\_zoned\_clean added (@ciB89)
* Vacuum: Carpet mode support (@rytilahti)
* WiFi Repeater: WiFi roaming and signal strange indicator added (@syssi)

[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.3.9...0.4.0)

**Implemented enhancements:**

- Extend the Air Quality Monitor PM2.5 support [\#283](https://github.com/rytilahti/python-miio/issues/283)
- Support for Xiaomi Mi Smart Electric Rice Cooker [\#282](https://github.com/rytilahti/python-miio/issues/282)
- Improved support of the Xiaomi Smart Fan [\#244](https://github.com/rytilahti/python-miio/issues/244)
- Extended support of the Philips LED Ceiling Lamp [\#209](https://github.com/rytilahti/python-miio/issues/209)
- Add JSON output for easier integration with other tools [\#98](https://github.com/rytilahti/python-miio/issues/98)
- Xiaomi Mi Water Purifier support [\#71](https://github.com/rytilahti/python-miio/issues/71)
- Xiaomi WiFi Speaker support [\#69](https://github.com/rytilahti/python-miio/issues/69)
- Air Quality Monitor: Full support of the night mode [\#294](https://github.com/rytilahti/python-miio/pull/294) ([syssi](https://github.com/syssi))

**Fixed bugs:**

- Unable to extract token from Android backup [\#138](https://github.com/rytilahti/python-miio/issues/138)
- Xiaomi-Philips Eyecare control fail [\#74](https://github.com/rytilahti/python-miio/issues/74)
- Working with water purifier [\#48](https://github.com/rytilahti/python-miio/issues/48)

**Closed issues:**

- miiocli: Provide an error message for unknown commands [\#327](https://github.com/rytilahti/python-miio/issues/327)
- miplug status crash [\#326](https://github.com/rytilahti/python-miio/issues/326)
- IR remote chuangmiir module [\#325](https://github.com/rytilahti/python-miio/issues/325)
- Qing Mi Smart Power Strip cannot be setup，device id is 04b8824e [\#318](https://github.com/rytilahti/python-miio/issues/318)
- I can not start mirobo [\#316](https://github.com/rytilahti/python-miio/issues/316)
- acpartner-v3 [\#312](https://github.com/rytilahti/python-miio/issues/312)
- Vacuum v1 new firmware [\#305](https://github.com/rytilahti/python-miio/issues/305)
- Xiaomi Power Strip V1 is unable to handle some V2 properties [\#302](https://github.com/rytilahti/python-miio/issues/302)
- TypeError: isinstance\(\) arg 2 must be a type or tuple of types [\#296](https://github.com/rytilahti/python-miio/issues/296)
- Extend the Power Strip support [\#286](https://github.com/rytilahti/python-miio/issues/286)
- when i try to send a command  [\#277](https://github.com/rytilahti/python-miio/issues/277)
- Obtain token for given IP address [\#263](https://github.com/rytilahti/python-miio/issues/263)
- Unable to discover the device  [\#259](https://github.com/rytilahti/python-miio/issues/259)
- xiaomi vaccum cleaner not responding [\#92](https://github.com/rytilahti/python-miio/issues/92)
- xiaomi vacuum, manual moving mode: duration definition incorrect [\#62](https://github.com/rytilahti/python-miio/issues/62)

**Merged pull requests:**

- Chuangmi Plug V3: Make a local copy of the available properties [\#330](https://github.com/rytilahti/python-miio/pull/330) ([syssi](https://github.com/syssi))
- miiocli: Handle unknown commands \(Closes: \#327\) [\#329](https://github.com/rytilahti/python-miio/pull/329) ([syssi](https://github.com/syssi))
- Fix a name clash of click\_common and the argument "command" [\#328](https://github.com/rytilahti/python-miio/pull/328) ([syssi](https://github.com/syssi))
- Update README [\#324](https://github.com/rytilahti/python-miio/pull/324) ([syssi](https://github.com/syssi))
- Migrate miplug cli to the new ChuangmiPlug class \(Fixes: \#296\) [\#323](https://github.com/rytilahti/python-miio/pull/323) ([syssi](https://github.com/syssi))
- Link to the Home Assistant custom component "xiaomi\_cooker" added [\#320](https://github.com/rytilahti/python-miio/pull/320) ([syssi](https://github.com/syssi))
- Improve the Xiaomi Rice Cooker support [\#319](https://github.com/rytilahti/python-miio/pull/319) ([syssi](https://github.com/syssi))
- Air Conditioning Companion: Rewrite a captured command before replay [\#317](https://github.com/rytilahti/python-miio/pull/317) ([syssi](https://github.com/syssi))
- Air Conditioning Companion: Led property fixed [\#315](https://github.com/rytilahti/python-miio/pull/315) ([syssi](https://github.com/syssi))
- mDNS names of the cooker fixed [\#314](https://github.com/rytilahti/python-miio/pull/314) ([syssi](https://github.com/syssi))
- mDNS names of the Air Conditioning Companion \(AC partner\) added [\#313](https://github.com/rytilahti/python-miio/pull/313) ([syssi](https://github.com/syssi))
- Added new commands app\_goto\_target and app\_zoned\_clean [\#310](https://github.com/rytilahti/python-miio/pull/310) ([ciB89](https://github.com/ciB89))
- Link to the Home Assistant custom component "xiaomi\_raw" added [\#309](https://github.com/rytilahti/python-miio/pull/309) ([syssi](https://github.com/syssi))
- Improved support of the Xiaomi Smart Fan [\#306](https://github.com/rytilahti/python-miio/pull/306) ([syssi](https://github.com/syssi))
- mDNS discovery: Xiaomi Smart Fans added [\#304](https://github.com/rytilahti/python-miio/pull/304) ([syssi](https://github.com/syssi))
- Xiaomi Power Strip V1 is unable to handle some V2 properties  [\#303](https://github.com/rytilahti/python-miio/pull/303) ([syssi](https://github.com/syssi))
- mDNS discovery: Additional Philips Candle Light added [\#301](https://github.com/rytilahti/python-miio/pull/301) ([syssi](https://github.com/syssi))
- Add support for vacuum's carpet mode, which requires a recent firmware version [\#299](https://github.com/rytilahti/python-miio/pull/299) ([rytilahti](https://github.com/rytilahti))
- Air Conditioning Companion: Extended parsing of model and state [\#297](https://github.com/rytilahti/python-miio/pull/297) ([syssi](https://github.com/syssi))
- Air Quality Monitor: Type and payload example of the time\_state property updated [\#293](https://github.com/rytilahti/python-miio/pull/293) ([syssi](https://github.com/syssi))
- WiFi Speaker support improved [\#291](https://github.com/rytilahti/python-miio/pull/291) ([syssi](https://github.com/syssi))
- Imports optimized [\#290](https://github.com/rytilahti/python-miio/pull/290) ([syssi](https://github.com/syssi))
- Support of the unified command line interface for all devices [\#289](https://github.com/rytilahti/python-miio/pull/289) ([syssi](https://github.com/syssi))
- Power Strip support extended by additional attributes [\#288](https://github.com/rytilahti/python-miio/pull/288) ([syssi](https://github.com/syssi))
- Basic support for Xiaomi Mi Smart Electric Rice Cooker [\#287](https://github.com/rytilahti/python-miio/pull/287) ([syssi](https://github.com/syssi))
- WiFi Repeater: Wifi roaming and signal strange indicator added [\#285](https://github.com/rytilahti/python-miio/pull/285) ([syssi](https://github.com/syssi))
- Preparation of release 0.3.9 [\#281](https://github.com/rytilahti/python-miio/pull/281) ([syssi](https://github.com/syssi))
- Unified and scalable command line interface [\#191](https://github.com/rytilahti/python-miio/pull/191) ([yawor](https://github.com/yawor))


## [0.3.9](https://github.com/rytilahti/python-miio/tree/0.3.9)

This release provides support for some new devices, improved support of existing devices and various fixes.

New devices:
* Xiaomi Mi WiFi Repeater 2 (@syssi)
* Xiaomi Philips Zhirui Smart LED Bulb E14 Candle Lamp (@syssi)

Improvements:
* Repr of the AirPurifierStatus fixed (@sq5gvm)
* Chuangmi Plug V1, V2, V3 and M1 merged into a common class (@syssi)
* Water Purifier: Some properties added (@syssi)
* Air Conditioning Companion: LED status fixed (@syssi)
* Air Conditioning Companion: Target temperature property renamed (@syssi)
* Air Conditioning Companion: Swing mode property returns the enum now (@syssi)
* Move some generic util functions from vacuumcontainers to utils module (@rytilahti)
* Construct version bumped (@syssi)

[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.3.8...0.3.9)

**Closed issues:**

- Xiaomi Mi WiFi Amplifier 2 support [\#275](https://github.com/rytilahti/python-miio/issues/275)
- TypeError: not enough arguments for format string in airpurifier.py [\#264](https://github.com/rytilahti/python-miio/issues/264)
- Issue vaccum gen 2 - HA 0.64 -\> 0.65 Python 3.6.0 -\> 3.7.0 [\#261](https://github.com/rytilahti/python-miio/issues/261)
- Add support for Xiaomi Philips Zhirui Smart LED Bulb E14 Candle Lamp [\#243](https://github.com/rytilahti/python-miio/issues/243)
- Basic support for the Yeelight LED Ceiling Lamp v4 [\#240](https://github.com/rytilahti/python-miio/issues/240)
- from Construct developer, a note [\#222](https://github.com/rytilahti/python-miio/issues/222)

**Merged pull requests:**

- construct version bumped [\#280](https://github.com/rytilahti/python-miio/pull/280) ([syssi](https://github.com/syssi))
- Support for the Xiaomi Mi WiFi Repeater 2 added [\#278](https://github.com/rytilahti/python-miio/pull/278) ([syssi](https://github.com/syssi))
- Move some generic util functions from vacuumcontainers to utils module [\#276](https://github.com/rytilahti/python-miio/pull/276) ([rytilahti](https://github.com/rytilahti))
- Air Conditioning Companion: Swing mode property returns the enum now [\#274](https://github.com/rytilahti/python-miio/pull/274) ([syssi](https://github.com/syssi))
- Air Conditioning Companion: Target temperature property properly named [\#273](https://github.com/rytilahti/python-miio/pull/273) ([syssi](https://github.com/syssi))
- Air Conditioning Companion: LED status fixed [\#272](https://github.com/rytilahti/python-miio/pull/272) ([syssi](https://github.com/syssi))
- Water Purifier: Some properties added [\#271](https://github.com/rytilahti/python-miio/pull/271) ([syssi](https://github.com/syssi))
- Merge of the Chuangmi Plug V1, V2, V3 and M1 [\#270](https://github.com/rytilahti/python-miio/pull/270) ([syssi](https://github.com/syssi))
- Improve test coverage [\#269](https://github.com/rytilahti/python-miio/pull/269) ([syssi](https://github.com/syssi))
- Support for Xiaomi Philips Zhirui Smart LED Bulb E14 Candle Lamp [\#268](https://github.com/rytilahti/python-miio/pull/268) ([syssi](https://github.com/syssi))
- Air Purifier: Duplicate property removed from \_\_repr\_\_ [\#267](https://github.com/rytilahti/python-miio/pull/267) ([syssi](https://github.com/syssi))
- Tests for reprs of the status classes [\#266](https://github.com/rytilahti/python-miio/pull/266) ([syssi](https://github.com/syssi))
- Repr of the AirPurifierStatus fixed [\#265](https://github.com/rytilahti/python-miio/pull/265) ([sq5gvm](https://github.com/sq5gvm))


## [0.3.8](https://github.com/rytilahti/python-miio/tree/0.3.8)

Goodbye Python 3.4! This release marks end of support for python versions older than 3.5, paving a way for cleaner code and a nicer API for a future asyncio support. Highlights of this release:

* Support for several new devices, improvements to existing devices and various fixes thanks to @syssi.

* Firmware updates for vacuums (@rytilahti), the most prominent use case being installing custom firmwares (e.g. for rooting your device). Installing sound packs is also streamlined with a self-hosting server.

* The protocol quirks handling was extended to handle invalid messages from the cloud (thanks @jschmer), improving interoperability for Dustcloud.

New devices:
* Chuangmi Plug V3 (@syssi)
* Xiaomi Air Humidifier CA (@syssi)
* Xiaomi Air Purifier V3 (@syssi)
* Xiaomi Philips LED Ceiling Light 620mm (@syssi)

Improvements:
* Provide the mac address as property of the device info (@syssi)
* Air Purifier: button_pressed property added (@syssi)
* Generalize and move configure\_wifi to the Device class (@rytilahti)
* Power Strip: The wifi led and power price can be controlled now (@syssi)
* Try to fix decrypted payload quirks if it fails to parse as json (@jschmer)
* Air Conditioning Companion: Turn on/off and LED property added, load power fixed (@syssi)
* Strict check for version equality of construct (@arekbulski)
* Firmware update functionality (@rytilahti)

[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.3.7...0.3.8)

**Closed issues:**

- Can't retrieve token from Android app [\#246](https://github.com/rytilahti/python-miio/issues/246)
- Unsupported device found!  chuangmi.ir.v2 [\#242](https://github.com/rytilahti/python-miio/issues/242)
- Improved support of the Air Humidifier [\#241](https://github.com/rytilahti/python-miio/issues/241)
- Add support for the Xiaomi Philips LED Ceiling Light 620mm \(philips.light.zyceiling\) [\#234](https://github.com/rytilahti/python-miio/issues/234)
- Support Xiaomi Air Purifier v3 [\#231](https://github.com/rytilahti/python-miio/issues/231)

**Merged pull requests:**

- Add --ip for install\_sound, update\_firmware & update docs [\#262](https://github.com/rytilahti/python-miio/pull/262) ([rytilahti](https://github.com/rytilahti))
- Provide the mac address as property of the device info [\#260](https://github.com/rytilahti/python-miio/pull/260) ([syssi](https://github.com/syssi))
- Tests: Non-essential code removed [\#258](https://github.com/rytilahti/python-miio/pull/258) ([syssi](https://github.com/syssi))
- Support of the Chuangmi Plug V3  [\#257](https://github.com/rytilahti/python-miio/pull/257) ([syssi](https://github.com/syssi))
- Air Purifier V3: Response example updated [\#255](https://github.com/rytilahti/python-miio/pull/255) ([syssi](https://github.com/syssi))
- Support of the Air Purifier V3 added \(Closes: \#231\) [\#254](https://github.com/rytilahti/python-miio/pull/254) ([syssi](https://github.com/syssi))
- Air Purifier: Property "button\_pressed" added [\#253](https://github.com/rytilahti/python-miio/pull/253) ([syssi](https://github.com/syssi))
- Respond with an error after the retry counter is down to zero, log retries into debug logger [\#252](https://github.com/rytilahti/python-miio/pull/252) ([rytilahti](https://github.com/rytilahti))
- Drop python 3.4 support, which paves a way for nicer API for asyncio among other things [\#251](https://github.com/rytilahti/python-miio/pull/251) ([rytilahti](https://github.com/rytilahti))
- Generalize and move configure\_wifi to the Device class [\#250](https://github.com/rytilahti/python-miio/pull/250) ([rytilahti](https://github.com/rytilahti))
- Support of the Xiaomi Air Humidifier CA \(zhimi.humidifier.ca1\) [\#249](https://github.com/rytilahti/python-miio/pull/249) ([syssi](https://github.com/syssi))
- Xiaomi AC Companion: LED property added [\#248](https://github.com/rytilahti/python-miio/pull/248) ([syssi](https://github.com/syssi))
- Some misleading docstrings updated [\#245](https://github.com/rytilahti/python-miio/pull/245) ([syssi](https://github.com/syssi))
- Powerstrip support improved [\#239](https://github.com/rytilahti/python-miio/pull/239) ([syssi](https://github.com/syssi))
- Repr of the AirQualityMonitorStatus fixed [\#238](https://github.com/rytilahti/python-miio/pull/238) ([syssi](https://github.com/syssi))
- mDNS discovery: Additional philips light added [\#237](https://github.com/rytilahti/python-miio/pull/237) ([syssi](https://github.com/syssi))
- Try to fix decrypted payload quirks if it fails to parse as json [\#236](https://github.com/rytilahti/python-miio/pull/236) ([jschmer](https://github.com/jschmer))
- Device support of the Xiaomi Air Conditioning Companion improved [\#233](https://github.com/rytilahti/python-miio/pull/233) ([syssi](https://github.com/syssi))
- Construct related, strict check for version equality [\#232](https://github.com/rytilahti/python-miio/pull/232) ([arekbulski](https://github.com/arekbulski))
- Implement firmware update functionality [\#153](https://github.com/rytilahti/python-miio/pull/153) ([rytilahti](https://github.com/rytilahti))

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
