# Change Log

## [0.5.12](https://github.com/rytilahti/python-miio/tree/0.5.12) (2022-07-18)

Release highlights:

* Thanks to @starkillerOG, this library now supports event handling using `miio.PushServer`,
  making it possible to support instantenous event-based callbacks on supported devices.
  This works by leveraging the scene functionality for subscribing to events, and is
  at the moment only known to be supported by gateway devices.
  See the documentation for details: https://python-miio.readthedocs.io/en/latest/push_server.html

* Optional support for obtaining tokens from the cloud (using `micloud` library by @Squachen),
  making onboarding new devices out-of-the-box simpler than ever.
  You can access this feature using `miiocli cloud` command, or through `miio.CloudInterface` API.

* And of course support for new devices, various enhancements to existing ones as well as bug fixes

Thanks to all 20 individual contributors for this release, see the full changelog below for details!

[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.5.11...0.5.12)

**Breaking changes:**

- Require click8+ \(API incompatibility on result\_callback\) [\#1378](https://github.com/rytilahti/python-miio/pull/1378) (@Sir-Photch)
- Move yeelight to integrations.light package [\#1367](https://github.com/rytilahti/python-miio/pull/1367) (@rytilahti)
- Move humidifier implementations to miio.integrations.humidifier package [\#1365](https://github.com/rytilahti/python-miio/pull/1365) (@rytilahti)
- Move airpurifier impls to miio.integrations.airpurifier package [\#1364](https://github.com/rytilahti/python-miio/pull/1364) (@rytilahti)

**Implemented enhancements:**

- Implement fetching device tokens from the cloud [\#1460](https://github.com/rytilahti/python-miio/pull/1460) (@rytilahti)
- Implement push notifications for gateway [\#1459](https://github.com/rytilahti/python-miio/pull/1459) (@starkillerOG)
- Add soundpack install support for vacuum/dreame [\#1457](https://github.com/rytilahti/python-miio/pull/1457) (@GH0st3rs)
- Improve gateway get\_devices\_from\_dict [\#1456](https://github.com/rytilahti/python-miio/pull/1456) (@starkillerOG)
- Improved fanspeed mapping for Roborock S7 MaxV  [\#1454](https://github.com/rytilahti/python-miio/pull/1454) (@arthur-morgan-1)
- Add push server implementation to enable event handling [\#1446](https://github.com/rytilahti/python-miio/pull/1446) (@starkillerOG)
- Add yeelink.light.color7 for yeelight [\#1426](https://github.com/rytilahti/python-miio/pull/1426) (@rytilahti)
- vacuum/roborock: Allow custom timer ids [\#1423](https://github.com/rytilahti/python-miio/pull/1423) (@rytilahti)
- Add fan speed presets to VacuumInterface [\#1405](https://github.com/rytilahti/python-miio/pull/1405) (@2pirko)
- Add device\_id property to Device class [\#1384](https://github.com/rytilahti/python-miio/pull/1384) (@starkillerOG)
- Add common interface for vacuums [\#1368](https://github.com/rytilahti/python-miio/pull/1368) (@2pirko)
- roborock: auto empty dustbin support [\#1188](https://github.com/rytilahti/python-miio/pull/1188) (@craigcabrey)

**Fixed bugs:**

- Consolidate supported models for class and instance properties [\#1462](https://github.com/rytilahti/python-miio/pull/1462) (@rytilahti)
- fix lumi.plug.mmeu01 ZNCZ04LM [\#1449](https://github.com/rytilahti/python-miio/pull/1449) (@starkillerOG)
- Add quirk fix for double-oh values [\#1438](https://github.com/rytilahti/python-miio/pull/1438) (@rytilahti)
- Use result\_callback \(click8+\) in roborock integration [\#1390](https://github.com/rytilahti/python-miio/pull/1390) (@DoganM95)
- Retry on error code -9999 [\#1363](https://github.com/rytilahti/python-miio/pull/1363) (@rytilahti)
- Catch exceptions during quirk handling [\#1360](https://github.com/rytilahti/python-miio/pull/1360) (@rytilahti)
- Use devinfo.model for unsupported model warning
 [\#1359](https://github.com/rytilahti/python-miio/pull/1359) (@MPThLee)

**New devices:**

- Add support for Xiaomi Smart Standing Fan 2 Pro \(dmaker.fan.p33\) [\#1467](https://github.com/rytilahti/python-miio/pull/1467) (@dainnilsson)
- add zhimi.airpurifier.amp1 support [\#1464](https://github.com/rytilahti/python-miio/pull/1464) (@dsh0416)
- roborock: Add support for Roborock G10S \(roborock.vacuum.a46\) [\#1437](https://github.com/rytilahti/python-miio/pull/1437) (@rytilahti)
- Add support for Smartmi Air Purifier \(zhimi.airpurifier.za1\) [\#1417](https://github.com/rytilahti/python-miio/pull/1417) (@julian-klode)
- Add zhimi.airp.rmb1 support [\#1402](https://github.com/rytilahti/python-miio/pull/1402) (@jedziemyjedziemy)
- Add zhimi.airp.vb4 support \(air purifier 4 pro\) [\#1399](https://github.com/rytilahti/python-miio/pull/1399) (@rperrell)
- Add support for dreame.vacuum.p2150o [\#1382](https://github.com/rytilahti/python-miio/pull/1382) (@icepie)
- Add support for Air Purifier 4 \(zhimi.airp.mb5\) [\#1357](https://github.com/rytilahti/python-miio/pull/1357) (@MPThLee)
- Support for Xiaomi Vaccum Mop 2 Ultra and Pro+ \(dreame\) [\#1356](https://github.com/rytilahti/python-miio/pull/1356) (@2pirko)

**Documentation updates:**

- Various documentation cleanups [\#1466](https://github.com/rytilahti/python-miio/pull/1466) (@rytilahti)
- Remove docs for now-removed mi{ceil,plug,eyecare} cli tools [\#1465](https://github.com/rytilahti/python-miio/pull/1465) (@rytilahti)
- Fix outdated vacuum mentions in README [\#1442](https://github.com/rytilahti/python-miio/pull/1442) (@rytilahti)
- Update troubleshooting to note discovery issues with roborock.vacuum.a27 [\#1414](https://github.com/rytilahti/python-miio/pull/1414) (@golddragon007)
- Add cloud extractor for token extraction to documentation [\#1383](https://github.com/rytilahti/python-miio/pull/1383) (@NiRi0004)

**Merged pull requests:**

- Mark zhimi.airp.mb3a as supported [\#1468](https://github.com/rytilahti/python-miio/pull/1468) (@rytilahti)
- Disable 3.11-dev builds on mac and windows [\#1461](https://github.com/rytilahti/python-miio/pull/1461) (@rytilahti)
- Fix doc8 regression [\#1458](https://github.com/rytilahti/python-miio/pull/1458) (@rytilahti)
- Disable fail-fast on CI tests [\#1450](https://github.com/rytilahti/python-miio/pull/1450) (@rytilahti)
- Mark roborock q5 \(roborock.vacuum.a34\) as supported [\#1448](https://github.com/rytilahti/python-miio/pull/1448) (@rytilahti)
- zhimi\_miot: Rename fan\_speed to speed [\#1439](https://github.com/rytilahti/python-miio/pull/1439) (@syssi)
- Add viomi.vacuum.v13 for viomivacuum [\#1432](https://github.com/rytilahti/python-miio/pull/1432) (@rytilahti)
- Add python 3.11-dev to CI [\#1427](https://github.com/rytilahti/python-miio/pull/1427) (@rytilahti)
- Add codeql checks [\#1403](https://github.com/rytilahti/python-miio/pull/1403) (@rytilahti)
- Update pre-commit hooks to fix black in CI [\#1380](https://github.com/rytilahti/python-miio/pull/1380) (@rytilahti)
- Mark chuangmi.camera.038a2 as supported [\#1371](https://github.com/rytilahti/python-miio/pull/1371) (@rockyzhang)
- Mark roborock.vacuum.c1 as supported [\#1370](https://github.com/rytilahti/python-miio/pull/1370) (@rytilahti)
- Use integration type specific imports [\#1366](https://github.com/rytilahti/python-miio/pull/1366) (@rytilahti)
- Mark dmaker.fan.p{15,18} as supported [\#1362](https://github.com/rytilahti/python-miio/pull/1362) (@rytilahti)
- Mark philips.light.sread2 as supported for philips\_eyecare [\#1355](https://github.com/rytilahti/python-miio/pull/1355) (@rytilahti)
- Use \_mappings for all miot integrations [\#1349](https://github.com/rytilahti/python-miio/pull/1349) (@rytilahti)


## [0.5.11](https://github.com/rytilahti/python-miio/tree/0.5.11) (2022-03-07)

This release fixes zhimi.fan.za5 support and makes all integrations introspectable for their supported models.
For developers, there is now a network trace parser (in devtools/parse_pcap.py) that prints the decrypted the traffic for given tokens.

The following previously deprecated classes in favor of model-based discovery, if you were using these classes directly you need to adjust your code:
* AirFreshVA4 - use AirFresh
* AirHumidifierCA1, AirHumidifierCB1, AirHumidifierCB2 - use AirHumidifier
* AirDogX5, AirDogX7SM - use AirDogX3
* AirPurifierMB4 - use AirPurifierMiot
* Plug, PlugV1, PlugV3 - use ChuangmiPlug
* FanP9, FanP10, FanP11 - use FanMiot
* DreameVacuumMiot - use DreameVacuum
* Vacuum - use RoborockVacuum

[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.5.10...0.5.11)

**Breaking changes:**

- Remove deprecated integration classes [\#1343](https://github.com/rytilahti/python-miio/pull/1343) (@rytilahti)

**Implemented enhancements:**

- Add PCAP file parser for protocol analysis [\#1331](https://github.com/rytilahti/python-miio/pull/1331) (@rytilahti)

**Fixed bugs:**

- Fix bug for zhimi.fan.za5 resulting in user ack timeout [\#1348](https://github.com/rytilahti/python-miio/pull/1348) (@saxel)

**Deprecated:**

- Deprecate wifi\_led in favor of led [\#1342](https://github.com/rytilahti/python-miio/pull/1342) (@rytilahti)

**Merged pull requests:**

- Make sure miotdevice implementations define supported models [\#1345](https://github.com/rytilahti/python-miio/pull/1345) (@rytilahti)
- Add Viomi V2 \(viomi.vacuum.v6\) as supported [\#1340](https://github.com/rytilahti/python-miio/pull/1340) (@rytilahti)
- Mark Roborock S7 MaxV \(roborock.vacuum.a27\) as supported [\#1337](https://github.com/rytilahti/python-miio/pull/1337) (@rytilahti)
- Add pyupgrade to CI runs [\#1329](https://github.com/rytilahti/python-miio/pull/1329) (@rytilahti)


## [0.5.10](https://github.com/rytilahti/python-miio/tree/0.5.10) (2022-02-17)

This release adds support for several new devices (see details below, thanks to @PRO-2684, @peleccom, @ymj0424, and @supar), and contains improvements to Roborock S7, yeelight and gateway integrations (thanks to @starkillerOG, @Kirmas, and @shred86). Thanks also to everyone who has reported their working model information, we can use this information to provide better discovery in the future and this release silences the warning for known working models.

Python 3.6 is no longer supported, and Fan{V2,SA1,ZA1,ZA3,ZA4} utility classes are now removed in favor of using Fan class.

[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.5.9.2...0.5.10)

**Breaking changes:**

- Split fan.py to vendor-specific fan integrations [\#1304](https://github.com/rytilahti/python-miio/pull/1304) (@rytilahti)
- Drop python 3.6 support [\#1263](https://github.com/rytilahti/python-miio/pull/1263) (@rytilahti)

**Implemented enhancements:**

- Improve miotdevice mappings handling [\#1302](https://github.com/rytilahti/python-miio/pull/1302) (@rytilahti)
- airpurifier\_miot: force aqi update prior fetching data [\#1282](https://github.com/rytilahti/python-miio/pull/1282) (@rytilahti)
- improve gateway error messages [\#1261](https://github.com/rytilahti/python-miio/pull/1261) (@starkillerOG)
- yeelight: use and expose the color temp range from specs [\#1247](https://github.com/rytilahti/python-miio/pull/1247) (@Kirmas)
- Add Roborock S7 mop scrub intensity [\#1236](https://github.com/rytilahti/python-miio/pull/1236) (@shred86)

**New devices:**

- Add support for zhimi.heater.za2 [\#1301](https://github.com/rytilahti/python-miio/pull/1301) (@PRO-2684)
- Dreame F9 Vacuum \(dreame.vacuum.p2008\) support [\#1290](https://github.com/rytilahti/python-miio/pull/1290) (@peleccom)
- Add support for Air Purifier 4 Pro \(zhimi.airp.va2\) [\#1287](https://github.com/rytilahti/python-miio/pull/1287) (@ymj0424)
- Add support for deerma.humidifier.jsq{s,5} [\#1193](https://github.com/rytilahti/python-miio/pull/1193) (@supar)

**Merged pull requests:**

- Add roborock.vacuum.a23 to supported models [\#1314](https://github.com/rytilahti/python-miio/pull/1314) (@rytilahti)
- Move philips light implementations to integrations/light/philips [\#1306](https://github.com/rytilahti/python-miio/pull/1306) (@rytilahti)
- Move leshow fan implementation to integrations/fan/leshow/ [\#1305](https://github.com/rytilahti/python-miio/pull/1305) (@rytilahti)
- Split fan\_miot.py to vendor-specific fan integrations [\#1303](https://github.com/rytilahti/python-miio/pull/1303) (@rytilahti)
- Add chuangmi.remote.v2 to chuangmiir [\#1299](https://github.com/rytilahti/python-miio/pull/1299) (@rytilahti)
- Perform pypi release on github release [\#1298](https://github.com/rytilahti/python-miio/pull/1298) (@rytilahti)
- Print debug recv contents prior accessing its contents [\#1293](https://github.com/rytilahti/python-miio/pull/1293) (@rytilahti)
- Add more supported models [\#1292](https://github.com/rytilahti/python-miio/pull/1292) (@rytilahti)
- Add more supported models [\#1275](https://github.com/rytilahti/python-miio/pull/1275) (@rytilahti)
- Update installation instructions to use poetry [\#1259](https://github.com/rytilahti/python-miio/pull/1259) (@rytilahti)
- Add more supported models based on discovery.py's mdns records [\#1258](https://github.com/rytilahti/python-miio/pull/1258) (@rytilahti)

## [0.5.9.2](https://github.com/rytilahti/python-miio/tree/0.5.9.2) (2021-12-14)

This release fixes regressions caused by the recent refactoring related to supported models:
* philips_bulb now defaults to a bulb that has color temperature setting
* gateway devices do not perform an info query as that is handled by their parent

Also, the list of the supported models was extended thanks to the feedback from the community!

[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.5.9.1...0.5.9.2)

**Implemented enhancements:**

- Add yeelink.bhf\_light.v2 and yeelink.light.lamp22 support [\#1250](https://github.com/rytilahti/python-miio/pull/1250) ([FaintGhost](https://github.com/FaintGhost))
- Skip warning if the unknown model is reported on a base class [\#1243](https://github.com/rytilahti/python-miio/pull/1243) ([rytilahti](https://github.com/rytilahti))
- Add emptying bin status for roborock s7+ [\#1190](https://github.com/rytilahti/python-miio/pull/1190) ([rytilahti](https://github.com/rytilahti))

**Fixed bugs:**

- Fix Roborock S7 fan speed [\#1235](https://github.com/rytilahti/python-miio/pull/1235) ([shred86](https://github.com/shred86))
- gateway: remove click support for gateway devices [\#1229](https://github.com/rytilahti/python-miio/pull/1229) ([starkillerOG](https://github.com/starkillerOG))
- mirobo: make sure config always exists [\#1207](https://github.com/rytilahti/python-miio/pull/1207) ([rytilahti](https://github.com/rytilahti))
- Fix typo [\#1204](https://github.com/rytilahti/python-miio/pull/1204) ([com30n](https://github.com/com30n))

**Merged pull requests:**

- philips\_eyecare: add philips.light.sread1 as supported [\#1246](https://github.com/rytilahti/python-miio/pull/1246) ([rytilahti](https://github.com/rytilahti))
- Add yeelink.light.color3 support [\#1245](https://github.com/rytilahti/python-miio/pull/1245) ([Kirmas](https://github.com/Kirmas))
- Use codecov-action@v2 for CI [\#1244](https://github.com/rytilahti/python-miio/pull/1244) ([rytilahti](https://github.com/rytilahti))
- Add yeelink.light.color5 support [\#1242](https://github.com/rytilahti/python-miio/pull/1242) ([Kirmas](https://github.com/Kirmas))
- Add more supported devices to their corresponding classes [\#1237](https://github.com/rytilahti/python-miio/pull/1237) ([rytilahti](https://github.com/rytilahti))
- Add zhimi.humidfier.ca4 as supported model [\#1220](https://github.com/rytilahti/python-miio/pull/1220) ([jbouwh](https://github.com/jbouwh))
- vacuum: Add t7s \(roborock.vacuum.a14\) [\#1214](https://github.com/rytilahti/python-miio/pull/1214) ([rytilahti](https://github.com/rytilahti))
- philips\_bulb: add philips.light.downlight to supported devices [\#1212](https://github.com/rytilahti/python-miio/pull/1212) ([rytilahti](https://github.com/rytilahti))

## [0.5.9.1](https://github.com/rytilahti/python-miio/tree/0.5.9.1) (2021-12-01)

This minor release only adds already known models pre-emptively to the lists of supported models to avoid flooding the issue tracker on reports after the next homeassistant release.

[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.5.9...0.5.9.1)

**Merged pull requests:**

- Add known models to supported models [\#1202](https://github.com/rytilahti/python-miio/pull/1202) ([rytilahti](https://github.com/rytilahti))
- Add issue template for missing model information [\#1200](https://github.com/rytilahti/python-miio/pull/1200) ([rytilahti](https://github.com/rytilahti))


## [0.5.9](https://github.com/rytilahti/python-miio/tree/0.5.9) (2021-11-30)

Besides enhancements and bug fixes, this release includes plenty of janitoral work to enable common base classes in the future.

For library users:
* Integrations are slowly moving to their own packages and directories, e.g. the vacuum module is now located in `miio.integrations.vacuum.roborock`.
* Using `Vacuum` is now deprecated and will be later used as the common interface class for all vacuum implementations. For roborock vacuums, use `RoborockVacuum` instead.


[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.5.8...0.5.9)

**Breaking changes:**

- Move vacuums to self-contained integrations [\#1165](https://github.com/rytilahti/python-miio/pull/1165) ([rytilahti](https://github.com/rytilahti))
- Remove unnecessary subclass constructors, deprecate subclasses only setting the model [\#1146](https://github.com/rytilahti/python-miio/pull/1146) ([rytilahti](https://github.com/rytilahti))
- Remove deprecated cli tools \(plug,miceil,mieye\) [\#1130](https://github.com/rytilahti/python-miio/pull/1130) ([rytilahti](https://github.com/rytilahti))

**Implemented enhancements:**

- Upgrage install and pre-commit dependencies [\#1192](https://github.com/rytilahti/python-miio/pull/1192) ([rytilahti](https://github.com/rytilahti))
- Add py.typed to the package [\#1184](https://github.com/rytilahti/python-miio/pull/1184) ([rytilahti](https://github.com/rytilahti))
- airhumidifer\_\(mj\)jsq: Add use\_time for better API compatibility [\#1179](https://github.com/rytilahti/python-miio/pull/1179) ([rytilahti](https://github.com/rytilahti))
- vacuum: return none on is\_water\_box\_attached if unsupported [\#1178](https://github.com/rytilahti/python-miio/pull/1178) ([rytilahti](https://github.com/rytilahti))
- Add more supported vacuum models [\#1173](https://github.com/rytilahti/python-miio/pull/1173) ([OGKevin](https://github.com/OGKevin))
- Reorganize yeelight specs file [\#1166](https://github.com/rytilahti/python-miio/pull/1166) ([Kirmas](https://github.com/Kirmas))
- enable G1 vacuum for miiocli [\#1164](https://github.com/rytilahti/python-miio/pull/1164) ([ghoost82](https://github.com/ghoost82))
- Add light specs for yeelight [\#1163](https://github.com/rytilahti/python-miio/pull/1163) ([Kirmas](https://github.com/Kirmas))
- Add S5 MAX model to support models list. [\#1157](https://github.com/rytilahti/python-miio/pull/1157) ([OGKevin](https://github.com/OGKevin))
- Use poetry-core as build-system [\#1152](https://github.com/rytilahti/python-miio/pull/1152) ([rytilahti](https://github.com/rytilahti))
- Support for Xiaomi Mijia G1 \(mijia.vacuum.v2\)  [\#867](https://github.com/rytilahti/python-miio/pull/867) ([neturmel](https://github.com/neturmel))

**Fixed bugs:**

- Fix test\_properties command logic [\#1180](https://github.com/rytilahti/python-miio/pull/1180) ([Zuz666](https://github.com/Zuz666))
- Make sure all device-derived classes accept model kwarg [\#1143](https://github.com/rytilahti/python-miio/pull/1143) ([rytilahti](https://github.com/rytilahti))
- Make cli work again for offline gen1 vacs, fix tests [\#1141](https://github.com/rytilahti/python-miio/pull/1141) ([rytilahti](https://github.com/rytilahti))
- Fix `water_level` calculation for humidifiers [\#1140](https://github.com/rytilahti/python-miio/pull/1140) ([bieniu](https://github.com/bieniu))
- fix TypeError in gateway property exception handling [\#1138](https://github.com/rytilahti/python-miio/pull/1138) ([starkillerOG](https://github.com/starkillerOG))
- Do not get battery status for mains powered devices [\#1131](https://github.com/rytilahti/python-miio/pull/1131) ([starkillerOG](https://github.com/starkillerOG))

**Deprecated:**

- Deprecate roborock specific miio.Vacuum [\#1191](https://github.com/rytilahti/python-miio/pull/1191) ([rytilahti](https://github.com/rytilahti))

**New devices:**

- add support for smart pet water dispenser mmgg.pet\_waterer.s1 [\#1174](https://github.com/rytilahti/python-miio/pull/1174) ([ofen](https://github.com/ofen))

**Documentation updates:**

- Docs: Add workaround for file upload failure [\#1155](https://github.com/rytilahti/python-miio/pull/1155) ([martin-kokos](https://github.com/martin-kokos))
- Add examples how to avoid model autodetection [\#1142](https://github.com/rytilahti/python-miio/pull/1142) ([rytilahti](https://github.com/rytilahti))
- Restructure & improve documentation [\#1139](https://github.com/rytilahti/python-miio/pull/1139) ([rytilahti](https://github.com/rytilahti))

**Merged pull requests:**

- Add Air Purifier Pro H support [\#1185](https://github.com/rytilahti/python-miio/pull/1185) ([pvizeli](https://github.com/pvizeli))
- Allow publish on test pypi workflow to fail [\#1177](https://github.com/rytilahti/python-miio/pull/1177) ([rytilahti](https://github.com/rytilahti))
- Relax pyyaml version requirement [\#1176](https://github.com/rytilahti/python-miio/pull/1176) ([rytilahti](https://github.com/rytilahti))
- create separate directory for yeelight [\#1160](https://github.com/rytilahti/python-miio/pull/1160) ([Kirmas](https://github.com/Kirmas))
- Add workflow to publish packages on pypi [\#1145](https://github.com/rytilahti/python-miio/pull/1145) ([rytilahti](https://github.com/rytilahti))
- Add tests for DeviceInfo [\#1144](https://github.com/rytilahti/python-miio/pull/1144) ([rytilahti](https://github.com/rytilahti))
- Mark device\_classes inside devicegroupmeta as private [\#1129](https://github.com/rytilahti/python-miio/pull/1129) ([rytilahti](https://github.com/rytilahti))


## [0.5.8](https://github.com/rytilahti/python-miio/tree/0.5.8) (2021-09-01)

[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.5.7...0.5.8)

**Implemented enhancements:**

- vacuum: skip timezone call if there are no timers [\#1122](https://github.com/rytilahti/python-miio/pull/1122) ([rytilahti](https://github.com/rytilahti))

**Closed issues:**

- Smart Mi Standing fan 3 \(Xiaomi Pedestal Fan 3, zhimi.fan.za5\) [\#788](https://github.com/rytilahti/python-miio/issues/788)

**Merged pull requests:**

- readme: add micloudfaker to list of related projects [\#1127](https://github.com/rytilahti/python-miio/pull/1127) ([unrelentingtech](https://github.com/unrelentingtech))
- Update readme with section for related projects [\#1126](https://github.com/rytilahti/python-miio/pull/1126) ([rytilahti](https://github.com/rytilahti))
- add lumi.plug.mmeu01 - ZNCZ04LM [\#1125](https://github.com/rytilahti/python-miio/pull/1125) ([starkillerOG](https://github.com/starkillerOG))
- Do not use deprecated `depth` property [\#1124](https://github.com/rytilahti/python-miio/pull/1124) ([bieniu](https://github.com/bieniu))
- vacuum: remove long-deprecated 'return\_list' for clean\_details [\#1123](https://github.com/rytilahti/python-miio/pull/1123) ([rytilahti](https://github.com/rytilahti))
- deprecate Fan{V2,SA1,ZA1,ZA3,ZA4} in favor of model kwarg [\#1119](https://github.com/rytilahti/python-miio/pull/1119) ([rytilahti](https://github.com/rytilahti))
- Add support for Smartmi Standing Fan 3 \(zhimi.fan.za5\) [\#1087](https://github.com/rytilahti/python-miio/pull/1087) ([rnovatorov](https://github.com/rnovatorov))

## [0.5.7](https://github.com/rytilahti/python-miio/tree/0.5.7) (2021-08-13)

This release improves several integrations (including yeelight, airpurifier_miot, dreamevacuum, rockrobo) and adds support for Roidmi Eve vacuums, see the full changelog for more details.

Note that this will likely be the last release on the 0.5 series before breaking the API to reorganize the project structure and provide common device type specific interfaces.

[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.5.6...0.5.7)

**Implemented enhancements:**

- Add setting for carpet avoidance to vacuums [\#1040](https://github.com/rytilahti/python-miio/issues/1040)
- Add  optional "Length" parameter to chuangmi\_ir.py play\_raw\(\).  for "chuangmi.remote.v2" to send some command properly  [\#820](https://github.com/rytilahti/python-miio/issues/820)
- Add update\_service callback for zeroconf listener [\#1112](https://github.com/rytilahti/python-miio/pull/1112) ([rytilahti](https://github.com/rytilahti))
- Add rockrobo-vacuum-a10 to mdns discovery list [\#1110](https://github.com/rytilahti/python-miio/pull/1110) ([rytilahti](https://github.com/rytilahti))
- Added additional OperatingModes and FaultStatuses for dreamevacuum [\#1090](https://github.com/rytilahti/python-miio/pull/1090) ([StarterCraft](https://github.com/StarterCraft))
- yeelight: add dump\_ble\_debug [\#1053](https://github.com/rytilahti/python-miio/pull/1053) ([rytilahti](https://github.com/rytilahti))
- Convert codebase to pass mypy checks [\#1046](https://github.com/rytilahti/python-miio/pull/1046) ([rytilahti](https://github.com/rytilahti))
- Add optional length parameter to play\_\* for chuangmi\_ir [\#1043](https://github.com/rytilahti/python-miio/pull/1043) ([Dozku](https://github.com/Dozku))
- Add features for newer vacuums \(eg Roborock S7\) [\#1039](https://github.com/rytilahti/python-miio/pull/1039) ([fettlaus](https://github.com/fettlaus))

**Fixed bugs:**

- air purifier unknown oprating mode [\#1106](https://github.com/rytilahti/python-miio/issues/1106)
- Missing Listener method for current zeroconf library [\#1101](https://github.com/rytilahti/python-miio/issues/1101)
- DeviceError when trying to turn on my Xiaomi Mi Smart Pedestal Fan [\#1100](https://github.com/rytilahti/python-miio/issues/1100)
- Unable to discover vacuum cleaner: Xiaomi Mi Robot Vacuum Mop \(aka dreame.vacuum.mc1808\) [\#1086](https://github.com/rytilahti/python-miio/issues/1086)
- Crashes if no hw\_ver present [\#1084](https://github.com/rytilahti/python-miio/issues/1084)
- Viomi S9 does not expose hv\_wer [\#1082](https://github.com/rytilahti/python-miio/issues/1082)
- set\_rotate FanP10 sends the wrong command [\#1076](https://github.com/rytilahti/python-miio/issues/1076)
- Vacuum 1C STYTJ01ZHM \(dreame.vacuum.mc1808\) is not update, 0% battery [\#1069](https://github.com/rytilahti/python-miio/issues/1069)
- Requirement is pinned for python-miio 0.5.6: defusedxml\>=0.6,\<0.7 [\#1062](https://github.com/rytilahti/python-miio/issues/1062)
- Problem with dmaker.fan.1c [\#1036](https://github.com/rytilahti/python-miio/issues/1036)
- Yeelight Smart Dual Control Module \(yeelink.switch.sw1\) - discovered by HA but can not configure [\#1033](https://github.com/rytilahti/python-miio/issues/1033)
- Update-firmware not working for Roborock S5 [\#1000](https://github.com/rytilahti/python-miio/issues/1000)
- Roborock S7  [\#994](https://github.com/rytilahti/python-miio/issues/994)
- airpurifier\_miot: return OperationMode.Unknown if mode is unknown [\#1111](https://github.com/rytilahti/python-miio/pull/1111) ([rytilahti](https://github.com/rytilahti))
- Fix set\_rotate for dmaker.fan.p10 \(\#1076\) [\#1078](https://github.com/rytilahti/python-miio/pull/1078) ([pooyashahidi](https://github.com/pooyashahidi))

**Closed issues:**

- Xiaomi Roborock S6 MaxV [\#1108](https://github.com/rytilahti/python-miio/issues/1108)
- dreame.vacuum.mb1808 unsupported [\#1104](https://github.com/rytilahti/python-miio/issues/1104)
- The new way to get device token [\#1088](https://github.com/rytilahti/python-miio/issues/1088)
- Add Air Conditioning Partner 2 support [\#1058](https://github.com/rytilahti/python-miio/issues/1058)
- Please add support for the Mijia 1G Vacuum! [\#1057](https://github.com/rytilahti/python-miio/issues/1057)
- ble\_dbg\_tbl\_dump user ack timeout [\#1051](https://github.com/rytilahti/python-miio/issues/1051)
- Roborock S7 can't be added to Home Assistant [\#1041](https://github.com/rytilahti/python-miio/issues/1041)
- Cannot get status from my zhimi.airpurifier.mb3\(Airpurifier 3H\) [\#1037](https://github.com/rytilahti/python-miio/issues/1037)
- Xiaomi Mi Robot \(viomivacuum\), command stability [\#800](https://github.com/rytilahti/python-miio/issues/800)
- \[meta\] list of miot-enabled devices [\#627](https://github.com/rytilahti/python-miio/issues/627)

**Merged pull requests:**

- Fix cct\_max for ZNLDP12LM [\#1098](https://github.com/rytilahti/python-miio/pull/1098) ([mouth4war](https://github.com/mouth4war))
- deprecate old helper scripts in favor of miiocli [\#1096](https://github.com/rytilahti/python-miio/pull/1096) ([rytilahti](https://github.com/rytilahti))
- Add link to the Home Assistant custom component hass-xiaomi-miot [\#1095](https://github.com/rytilahti/python-miio/pull/1095) ([al-one](https://github.com/al-one))
- Update chuangmi\_ir.py to accept 2 arguments \(frequency and length\) [\#1091](https://github.com/rytilahti/python-miio/pull/1091) ([mpsOxygen](https://github.com/mpsOxygen))
- Add `water_level` and `water_tank_detached` property for humidifiers, deprecate `depth` [\#1089](https://github.com/rytilahti/python-miio/pull/1089) ([bieniu](https://github.com/bieniu))
- DeviceInfo refactor, do not crash on missing fields [\#1083](https://github.com/rytilahti/python-miio/pull/1083) ([rytilahti](https://github.com/rytilahti))
- Calculate `depth` for zhimi.humidifier.ca1 [\#1077](https://github.com/rytilahti/python-miio/pull/1077) ([bieniu](https://github.com/bieniu))
- increase socket buffer size 1024-\>4096 [\#1075](https://github.com/rytilahti/python-miio/pull/1075) ([starkillerOG](https://github.com/starkillerOG))
- Loosen defusedxml version requirement [\#1073](https://github.com/rytilahti/python-miio/pull/1073) ([rytilahti](https://github.com/rytilahti))
- Added support for Roidmi Eve [\#1072](https://github.com/rytilahti/python-miio/pull/1072) ([martin9000andersen](https://github.com/martin9000andersen))
- airpurifier\_miot: Move favorite\_rpm from MB4 to Basic [\#1070](https://github.com/rytilahti/python-miio/pull/1070) ([SylvainPer](https://github.com/SylvainPer))
- fix error on GATEWAY\_MODEL\_ZIG3 when no zigbee devices connected [\#1065](https://github.com/rytilahti/python-miio/pull/1065) ([starkillerOG](https://github.com/starkillerOG))
- add fan speed enum 106 as "Auto" for Roborock S6 MaxV [\#1063](https://github.com/rytilahti/python-miio/pull/1063) ([RubenKelevra](https://github.com/RubenKelevra))
- Add additional mode of Air Purifier Super 2 [\#1054](https://github.com/rytilahti/python-miio/pull/1054) ([daxingplay](https://github.com/daxingplay))
- Fix home\(\) for Roborock S7 [\#1050](https://github.com/rytilahti/python-miio/pull/1050) ([whig0](https://github.com/whig0))
- Added Roborock s7 to troubleshooting guide [\#1045](https://github.com/rytilahti/python-miio/pull/1045) ([Claustn](https://github.com/Claustn))
- Add github flow for ci [\#1044](https://github.com/rytilahti/python-miio/pull/1044) ([rytilahti](https://github.com/rytilahti))
- Improve Yeelight support \(expose more properties, add support for secondary lights\) [\#1035](https://github.com/rytilahti/python-miio/pull/1035) ([Kirmas](https://github.com/Kirmas))
- README.md improvements [\#1032](https://github.com/rytilahti/python-miio/pull/1032) ([rytilahti](https://github.com/rytilahti))

## [0.5.6](https://github.com/rytilahti/python-miio/tree/0.5.6) (2021-05-05)

[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.5.5.2...0.5.6)

**Implemented enhancements:**

- RFC: Add a script to simplify finding supported properties for miio [\#919](https://github.com/rytilahti/python-miio/issues/919)
- Improve test\_properties output [\#1024](https://github.com/rytilahti/python-miio/pull/1024) ([rytilahti](https://github.com/rytilahti))
- Relax zeroconf version requirement [\#1023](https://github.com/rytilahti/python-miio/pull/1023) ([rytilahti](https://github.com/rytilahti))
- Add test\_properties command to device class [\#1014](https://github.com/rytilahti/python-miio/pull/1014) ([rytilahti](https://github.com/rytilahti))
- Add discover command to miiocli [\#1013](https://github.com/rytilahti/python-miio/pull/1013) ([rytilahti](https://github.com/rytilahti))
- Fix supported oscillation angles of the dmaker.fan.p9 [\#1011](https://github.com/rytilahti/python-miio/pull/1011) ([syssi](https://github.com/syssi))
- Add additional operation mode of the deerma.humidifier.jsq1 [\#1010](https://github.com/rytilahti/python-miio/pull/1010) ([syssi](https://github.com/syssi))
- Roborock S7: Parse history details returned as dict [\#1006](https://github.com/rytilahti/python-miio/pull/1006) ([fettlaus](https://github.com/fettlaus))

**Fixed bugs:**

- zeroconf 0.29.0 which is incompatible [\#1022](https://github.com/rytilahti/python-miio/issues/1022)
- Remove superfluous decryption failure for handshake responses [\#1008](https://github.com/rytilahti/python-miio/issues/1008)
- Skip pausing on Roborock S50 [\#1005](https://github.com/rytilahti/python-miio/issues/1005)
- Roborock S7 after Firmware Update 4.1.2-0928 - KeyError [\#1004](https://github.com/rytilahti/python-miio/issues/1004)
- No air quality value when aqi is 1 [\#958](https://github.com/rytilahti/python-miio/issues/958)
- Fix exception on devices with removed lan\_ctrl [\#1028](https://github.com/rytilahti/python-miio/pull/1028) ([Kirmas](https://github.com/Kirmas))
- Fix start bug and improve error handling in walkingpad integration [\#1017](https://github.com/rytilahti/python-miio/pull/1017) ([dewgenenny](https://github.com/dewgenenny))
- gateway: fix zigbee lights [\#1016](https://github.com/rytilahti/python-miio/pull/1016) ([starkillerOG](https://github.com/starkillerOG))
- Silence unable to decrypt warning for handshake responses [\#1015](https://github.com/rytilahti/python-miio/pull/1015) ([rytilahti](https://github.com/rytilahti))
- Fix set\_mode\_and\_speed mode for airdog airpurifier [\#993](https://github.com/rytilahti/python-miio/pull/993) ([alexeypetrenko](https://github.com/alexeypetrenko))

**Closed issues:**

- Add Dafang camera \(isa.camera.df3\) support [\#996](https://github.com/rytilahti/python-miio/issues/996)
- Roborock S7 [\#989](https://github.com/rytilahti/python-miio/issues/989)
- WalkingPad A1 Pro [\#797](https://github.com/rytilahti/python-miio/issues/797)

**Merged pull requests:**

- Add basic dmaker.fan.1c support [\#1012](https://github.com/rytilahti/python-miio/pull/1012) ([syssi](https://github.com/syssi))
- Always return aqi value \[Revert PR\#930\] [\#1007](https://github.com/rytilahti/python-miio/pull/1007) ([bieniu](https://github.com/bieniu))
- Added S6 to skip pause on docking [\#1002](https://github.com/rytilahti/python-miio/pull/1002) ([Sian-Lee-SA](https://github.com/Sian-Lee-SA))
- Added number of dust collections to CleaningSummary if available [\#992](https://github.com/rytilahti/python-miio/pull/992) ([fettlaus](https://github.com/fettlaus))
- Reformat history data if returned as a dict/Roborock S7 Support \(\#989\) [\#990](https://github.com/rytilahti/python-miio/pull/990) ([fettlaus](https://github.com/fettlaus))
- Add support for Walkingpad A1 \(ksmb.walkingpad.v3\) [\#975](https://github.com/rytilahti/python-miio/pull/975) ([dewgenenny](https://github.com/dewgenenny))


## [0.5.5.2](https://github.com/rytilahti/python-miio/tree/0.5.5.2) (2021-03-24)

This release is mainly to re-add mapping parameter to MiotDevice constructor for backwards-compatibility reasons,
but adds also PyYAML dependency and improves MiOT support to allow limiting how many properties to query at once.

[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.5.5.1...0.5.5.2)

**Implemented enhancements:**

- Please add back the mapping parameter to `MiotDevice` constructor [\#982](https://github.com/rytilahti/python-miio/issues/982)

**Fixed bugs:**

- Missing dependency: pyyaml [\#986](https://github.com/rytilahti/python-miio/issues/986)

**Merged pull requests:**

- Add pyyaml dependency [\#987](https://github.com/rytilahti/python-miio/pull/987) ([rytilahti](https://github.com/rytilahti))
- Re-add mapping parameter to MiotDevice ctor [\#985](https://github.com/rytilahti/python-miio/pull/985) ([rytilahti](https://github.com/rytilahti))
- Move hardcoded parameter `max\_properties` [\#981](https://github.com/rytilahti/python-miio/pull/981) ([ha0y](https://github.com/ha0y))

## [0.5.5.1](https://github.com/rytilahti/python-miio/tree/0.5.5.1) (2021-03-20)

This release fixes a single regression of non-existing sequence file for those users who never used mirobo/miiocli vacuum previously.
Users of the library do not need this upgrade.

[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.5.5...0.5.5.1)

**Implemented enhancements:**

- Release new version of the library [\#969](https://github.com/rytilahti/python-miio/issues/969)
- Support for Mi Robot S1 [\#517](https://github.com/rytilahti/python-miio/issues/517)

**Fixed bugs:**

- Unable to decrypt token for S55 Vacuum [\#973](https://github.com/rytilahti/python-miio/issues/973)
- \[BUG\] No such file or directory: '/home/username/.cache/python-miio/python-mirobo.seq' when trying to update firmware [\#972](https://github.com/rytilahti/python-miio/issues/972)
- Fix wrong ordering of contextmanagers [\#976](https://github.com/rytilahti/python-miio/pull/976) ([rytilahti](https://github.com/rytilahti))

## [0.5.5](https://github.com/rytilahti/python-miio/tree/0.5.5) (2021-03-13)

This release adds support for several new devices, and contains improvements and fixes on several existing integrations.
Instead of summarizing all changes here, this library seeks to move completely automated changelogs based on the pull request tags to facilitate faster release cycles.
Until that happens, the full list of changes is listed below as usual.

[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.5.4...0.5.5)

**Implemented enhancements:**

- Connecting from external network [\#931](https://github.com/rytilahti/python-miio/issues/931)
- Filter out value 1 from the property AQI [\#925](https://github.com/rytilahti/python-miio/issues/925)
- Any plans on supporting Air Detector Lite PM2.5? [\#879](https://github.com/rytilahti/python-miio/issues/879)
- Get possible device commands/arguments via API [\#846](https://github.com/rytilahti/python-miio/issues/846)
- Add support for xiaomi scishare coffee machine [\#833](https://github.com/rytilahti/python-miio/issues/833)
- Make netifaces optional dependency [\#970](https://github.com/rytilahti/python-miio/pull/970) ([rytilahti](https://github.com/rytilahti))
- Unify subdevice types [\#947](https://github.com/rytilahti/python-miio/pull/947) ([starkillerOG](https://github.com/starkillerOG))
- Cleanup: add DeviceStatus to simplify status containers [\#941](https://github.com/rytilahti/python-miio/pull/941) ([rytilahti](https://github.com/rytilahti))
- add method to load subdevices from dict \(EU gateway support\) [\#936](https://github.com/rytilahti/python-miio/pull/936) ([starkillerOG](https://github.com/starkillerOG))
- Refactor & improve support for gateway devices [\#924](https://github.com/rytilahti/python-miio/pull/924) ([starkillerOG](https://github.com/starkillerOG))
- Add docformatter to pre-commit hooks [\#914](https://github.com/rytilahti/python-miio/pull/914) ([rytilahti](https://github.com/rytilahti))
- Improve MiotDevice API \(get\_property\_by, set\_property\_by, call\_action, call\_action\_by\) [\#905](https://github.com/rytilahti/python-miio/pull/905) ([rytilahti](https://github.com/rytilahti))
- Stopgap fix for miottemplate [\#902](https://github.com/rytilahti/python-miio/pull/902) ([rytilahti](https://github.com/rytilahti))
- Support resume\_or\_start for vacuum's segment cleaning [\#894](https://github.com/rytilahti/python-miio/pull/894) ([Sian-Lee-SA](https://github.com/Sian-Lee-SA))
- Add missing annotations for ViomiVacuum [\#872](https://github.com/rytilahti/python-miio/pull/872) ([dominikkarall](https://github.com/dominikkarall))
- Add generic \_\_repr\_\_ for Device class [\#869](https://github.com/rytilahti/python-miio/pull/869) ([rytilahti](https://github.com/rytilahti))
- Set timeout as parameter [\#866](https://github.com/rytilahti/python-miio/pull/866) ([titilambert](https://github.com/titilambert))
- Improve Viomi support \(status reporting, maps\) [\#808](https://github.com/rytilahti/python-miio/pull/808) ([titilambert](https://github.com/titilambert))

**Fixed bugs:**

- Make netifaces optional dependency [\#964](https://github.com/rytilahti/python-miio/issues/964)
- Some errors in miio/airdehumidifier.py [\#960](https://github.com/rytilahti/python-miio/issues/960)
- Roborock S5 Max not discovered [\#944](https://github.com/rytilahti/python-miio/issues/944)
- Vacuum timezone returns 'int' object is not subscriptable [\#921](https://github.com/rytilahti/python-miio/issues/921)
- discover\_devices doesnt work with xiaomi gateway v3 [\#916](https://github.com/rytilahti/python-miio/issues/916)
- Can control but not get info from the vacuum [\#912](https://github.com/rytilahti/python-miio/issues/912)
- airhumidifier\_miot.py - mapping attribute error [\#911](https://github.com/rytilahti/python-miio/issues/911)
- Xiaomi Humidifier CA4 fail to read status. \(zhimi.humidifier.ca4\) [\#908](https://github.com/rytilahti/python-miio/issues/908)
- miottemplate.py print specs.json fails [\#906](https://github.com/rytilahti/python-miio/issues/906)
- Miiocli and Airdog appliance [\#892](https://github.com/rytilahti/python-miio/issues/892)
- ServiceInfo has no attribute 'address' in miio/discovery [\#891](https://github.com/rytilahti/python-miio/issues/891)
- Devtools exception miottemplate.py generate [\#885](https://github.com/rytilahti/python-miio/issues/885)
- Issue with Xiaomi Miio gateway Integrations ZNDMWG03LM [\#864](https://github.com/rytilahti/python-miio/issues/864)
- Xiaomi Mi Robot Vacuum V1 - Fan Speed Issue [\#860](https://github.com/rytilahti/python-miio/issues/860)
- Xiaomi Smartmi Evaporation Air Humidifier 2 \(zhimi.humidifier.ca4\) [\#859](https://github.com/rytilahti/python-miio/issues/859)
- Report more specific exception when airdehumidifer is off [\#963](https://github.com/rytilahti/python-miio/pull/963) ([rytilahti](https://github.com/rytilahti))
- vacuum: second try to fix the timezone returning an integer [\#949](https://github.com/rytilahti/python-miio/pull/949) ([rytilahti](https://github.com/rytilahti))
- Fix the logic of staring cleaning a room for Viomi [\#946](https://github.com/rytilahti/python-miio/pull/946) ([AlexAlexPin](https://github.com/AlexAlexPin))
- vacuum: skip pausing on s50 and s6 maxv before return home call [\#933](https://github.com/rytilahti/python-miio/pull/933) ([rytilahti](https://github.com/rytilahti))
- Fix airpurifier\_airdog x5 and x7sm to derive from the x3 base class [\#903](https://github.com/rytilahti/python-miio/pull/903) ([rytilahti](https://github.com/rytilahti))
- Fix discovery for python-zeroconf 0.28+ [\#898](https://github.com/rytilahti/python-miio/pull/898) ([rytilahti](https://github.com/rytilahti))
- Vacuum: add fan speed preset for gen1 firmwares 3.5.8+ [\#893](https://github.com/rytilahti/python-miio/pull/893) ([mat4444](https://github.com/mat4444))

**Closed issues:**

- miiocli command not found [\#956](https://github.com/rytilahti/python-miio/issues/956)
- \[Roborock S6 MaxV\] Need a delay between pause and charge commands to return to dock [\#918](https://github.com/rytilahti/python-miio/issues/918)
- Support for Xiaomi Air purifier 3C [\#888](https://github.com/rytilahti/python-miio/issues/888)
- zhimi.heater.mc2 not fully supported [\#880](https://github.com/rytilahti/python-miio/issues/880)
- Support for leshow.fan.ss4 \(xiaomi Rosou SS4 Ventilator\) [\#806](https://github.com/rytilahti/python-miio/issues/806)
- Constant spam of: Unable to discover a device at address \[IP\] and Got exception while fetching the state: Unable to discover the device \[IP\] [\#407](https://github.com/rytilahti/python-miio/issues/407)
- Add documentation for miiocli [\#400](https://github.com/rytilahti/python-miio/issues/400)

**Merged pull requests:**

- Fix another typo in the docs [\#968](https://github.com/rytilahti/python-miio/pull/968) ([muellermartin](https://github.com/muellermartin))
- Fix link to API documentation [\#967](https://github.com/rytilahti/python-miio/pull/967) ([muellermartin](https://github.com/muellermartin))
- Add section for getting tokens from rooted devices [\#966](https://github.com/rytilahti/python-miio/pull/966) ([muellermartin](https://github.com/muellermartin))
- Improve airpurifier doc strings by adding raw responses [\#961](https://github.com/rytilahti/python-miio/pull/961) ([arturdobo](https://github.com/arturdobo))
- Add troubleshooting for Roborock app [\#954](https://github.com/rytilahti/python-miio/pull/954) ([lyghtnox](https://github.com/lyghtnox))
- Initial support for Vacuum 1C STYTJ01ZHM \(dreame.vacuum.mc1808\) [\#952](https://github.com/rytilahti/python-miio/pull/952) ([legacycode](https://github.com/legacycode))
- Replaced typing by pyyaml [\#945](https://github.com/rytilahti/python-miio/pull/945) ([legacycode](https://github.com/legacycode))
- janitoring: add bandit to pre-commit checks [\#940](https://github.com/rytilahti/python-miio/pull/940) ([rytilahti](https://github.com/rytilahti))
- vacuum: fallback to UTC when encountering unknown timezone response [\#932](https://github.com/rytilahti/python-miio/pull/932) ([rytilahti](https://github.com/rytilahti))
- \[miot air purifier\] Return None if aqi is 1 [\#930](https://github.com/rytilahti/python-miio/pull/930) ([bieniu](https://github.com/bieniu))
- added support for zhimi.humidifier.cb2 [\#917](https://github.com/rytilahti/python-miio/pull/917) ([sannoob](https://github.com/sannoob))
- Include some more flake8 checks [\#915](https://github.com/rytilahti/python-miio/pull/915) ([rytilahti](https://github.com/rytilahti))
- Improve miottemplate.py print to support python 3.7.3 \(Closes: \#906\) [\#910](https://github.com/rytilahti/python-miio/pull/910) ([syssi](https://github.com/syssi))
- Fix \_\_repr\_\_ of AirHumidifierMiotStatus \(Closes: \#908\) [\#909](https://github.com/rytilahti/python-miio/pull/909) ([syssi](https://github.com/syssi))
- Add clean mode \(new feature\) to the zhimi.humidifier.ca4 [\#907](https://github.com/rytilahti/python-miio/pull/907) ([syssi](https://github.com/syssi))
- Allow downloading miot spec files by model for miottemplate [\#904](https://github.com/rytilahti/python-miio/pull/904) ([rytilahti](https://github.com/rytilahti))
- Add Qingping Air Monitor Lite support \(cgllc.airm.cgdn1\) [\#900](https://github.com/rytilahti/python-miio/pull/900) ([arturdobo](https://github.com/arturdobo))
- Add support for Xiaomi Air purifier 3C  [\#899](https://github.com/rytilahti/python-miio/pull/899) ([arturdobo](https://github.com/arturdobo))
- Add support for zhimi.heater.mc2 [\#895](https://github.com/rytilahti/python-miio/pull/895) ([bafonins](https://github.com/bafonins))
- Add support for Yeelight Dual Control Module \(yeelink.switch.sw1\) [\#887](https://github.com/rytilahti/python-miio/pull/887) ([IhorSyerkov](https://github.com/IhorSyerkov))
- Retry and timeout can be change by setting a class attribute [\#884](https://github.com/rytilahti/python-miio/pull/884) ([titilambert](https://github.com/titilambert))
- Add support for all Huizuo Lamps \(w/ fans, heaters, and scenes\) [\#881](https://github.com/rytilahti/python-miio/pull/881) ([darckly](https://github.com/darckly))
- Add deerma.humidifier.jsq support [\#878](https://github.com/rytilahti/python-miio/pull/878) ([syssi](https://github.com/syssi))
- Export MiotDevice for miio module [\#876](https://github.com/rytilahti/python-miio/pull/876) ([syssi](https://github.com/syssi))
- Add missing "info" to device information query [\#873](https://github.com/rytilahti/python-miio/pull/873) ([rytilahti](https://github.com/rytilahti))
- Add Rosou SS4 Ventilator \(leshow.fan.ss4\) support [\#871](https://github.com/rytilahti/python-miio/pull/871) ([syssi](https://github.com/syssi))
- Initial support for HUIZUO PISCES For Bedroom [\#868](https://github.com/rytilahti/python-miio/pull/868) ([darckly](https://github.com/darckly))
- Add airdog.airpurifier.{x3,x5,x7sm} support [\#865](https://github.com/rytilahti/python-miio/pull/865) ([syssi](https://github.com/syssi))
- Add dmaker.airfresh.a1 support [\#862](https://github.com/rytilahti/python-miio/pull/862) ([syssi](https://github.com/syssi))
- Add support for Scishare coffee maker \(scishare.coffee.s1102\) [\#858](https://github.com/rytilahti/python-miio/pull/858) ([rytilahti](https://github.com/rytilahti))


## [0.5.4](https://github.com/rytilahti/python-miio/tree/0.5.4) (2020-11-15)

New devices:
* Xiaomi Smartmi Fresh Air System VA4 (zhimi.airfresh.va4) (@syssi)
* Xiaomi Mi Smart Pedestal Fan P9, P10, P11 (dmaker.fan.p9, dmaker.fan.p10, dmaker.fan.p11) (@swim2sun)
* Mijia Intelligent Sterilization Humidifier SCK0A45 (deerma.humidifier.jsq1)
* Air Conditioner Companion MCN (lumi.acpartner.mcn02) (@EugeneLiu)
* Xiaomi Water Purifier D1 (yunmi.waterpuri.lx9) and C1 (Triple Setting, yunmi.waterpuri.lx11) (@zhangjingye03)
* Xiaomi Mi Smart Air Conditioner A (xiaomi.aircondition.mc1, mc2, mc4 and mc5) (@zhangjingye03)
* Xiaomiyoupin Curtain Controller (Wi-Fi) / Aqara A1 (lumi.curtain.hagl05) (@in7egral)

Improvements:
* ViomiVacuum: New modes, states and error codes (@fs79)
* ViomiVacuum: Consumable status added (@titilambert)
* Gateway: Throws GatewayException in get\_illumination (@javicalle)
* Vacuum: Tangible User Interface (TUI) for the manual mode added (@rnovatorov)
* Vacuum: Mopping to VacuumingAndMopping renamed (@rytilahti)
* raw\_id moved from Vacuum to the Device base class (@rytilahti)
* \_\_json\_\_ boilerplate code from all status containers removed (@rytilahti)
* Pinned versions loosed and cryptography dependency bumped to new major version (@rytilahti)
* importlib\_metadata python\_version bounds corrected (@jonringer)
* CLI: EnumType defaults to incasesensitive now (@rytilahti)
* Better documentation and presentation of the documentation (@rytilahti)

Fixes:
* Vacuum: Invalid cron expression fixed (@rytilahti)
* Vacuum: Invalid cron elements handled gracefully (@rytilahti)
* Vacuum: WaterFlow as an enum defined (@rytilahti)
* Yeelight: Check color mode values for emptiness (@rytilahti)
* Airfresh: Temperature property of the zhimi.airfresh.va2 fixed (@syssi)
* Airfresh: PTC support of the dmaker.airfresh.t2017 fixed (@syssi)
* Airfresh: Payload of the boolean setter fixed (@syssi)
* Fan: Fan speed property of the dmaker.fan.p11 fixed (@iquix)


[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.5.3...0.5.4)

**Implemented enhancements:**

- Add error codes 2103 & 2105 [\#789](https://github.com/rytilahti/python-miio/issues/789)
- ViomiVacuumState 6 seems to be VaccuumMopping [\#783](https://github.com/rytilahti/python-miio/issues/783)
- Added some parameters: Error code, Viomimode, Viomibintype [\#799](https://github.com/rytilahti/python-miio/pull/799) ([fs79](https://github.com/fs79))
- Add mopping state & log a warning when encountering unknown state [\#784](https://github.com/rytilahti/python-miio/pull/784) ([rytilahti](https://github.com/rytilahti))

**Fixed bugs:**

- Invalid cron expression when using xiaomi\_miio integration in Home Assistant [\#847](https://github.com/rytilahti/python-miio/issues/847)
- viomivacuum doesn´t work with -o json\_pretty [\#816](https://github.com/rytilahti/python-miio/issues/816)
- yeeligth without color temperature status error [\#802](https://github.com/rytilahti/python-miio/issues/802)
- set\_waterflow roborock.vacuum.s5e [\#786](https://github.com/rytilahti/python-miio/issues/786)
- Requirement is pinned for python-miio 0.5.3: zeroconf\>=0.25.1,\<0.26.0 [\#780](https://github.com/rytilahti/python-miio/issues/780)
- Requirement is pinned for python-miio 0.5.3: pytz\>=2019.3,\<2020.0 [\#779](https://github.com/rytilahti/python-miio/issues/779)
- miiocli: remove network & AP information from info output [\#857](https://github.com/rytilahti/python-miio/pull/857) ([rytilahti](https://github.com/rytilahti))
- Fix PTC support of the dmaker.airfresh.t2017 [\#853](https://github.com/rytilahti/python-miio/pull/853) ([syssi](https://github.com/syssi))
- Vacuum: handle invalid cron elements gracefully [\#848](https://github.com/rytilahti/python-miio/pull/848) ([rytilahti](https://github.com/rytilahti))
- yeelight: Check color mode values for emptiness [\#829](https://github.com/rytilahti/python-miio/pull/829) ([rytilahti](https://github.com/rytilahti))
- Define WaterFlow as an enum [\#787](https://github.com/rytilahti/python-miio/pull/787) ([rytilahti](https://github.com/rytilahti))

**Closed issues:**

- Notify access support for MIoT Device [\#843](https://github.com/rytilahti/python-miio/issues/843)
- Xiaomi WiFi Power Plug\(Bluetooth Gateway\)\(chuangmi.plug.hmi208\) [\#840](https://github.com/rytilahti/python-miio/issues/840)
- Mi Air Purifier 3H - unable to connect [\#836](https://github.com/rytilahti/python-miio/issues/836)
- update-firmware on Xiaomi Mi Robot Vacuum V1 fails [\#818](https://github.com/rytilahti/python-miio/issues/818)
- Freash air system calibration of CO2 sensor command [\#814](https://github.com/rytilahti/python-miio/issues/814)
- Unable to discover the device \(zhimi.airpurifier.ma4\) [\#798](https://github.com/rytilahti/python-miio/issues/798)
- Mi Air Purifier 3H Timed out [\#796](https://github.com/rytilahti/python-miio/issues/796)
- Xiaomi Smartmi Fresh Air System XFXTDFR02ZM.   upgrade version of  XFXT01ZM with heater. [\#791](https://github.com/rytilahti/python-miio/issues/791)
- mi smart sensor gateway - check status [\#762](https://github.com/rytilahti/python-miio/issues/762)
- Installation problem 64bit [\#727](https://github.com/rytilahti/python-miio/issues/727)
- support dmaker.fan.p9 and dmaker.fan.p10 [\#721](https://github.com/rytilahti/python-miio/issues/721)
- Add support for lumi.acpartner.mcn02 please? [\#637](https://github.com/rytilahti/python-miio/issues/637)

**Merged pull requests:**

- Add deerma.humidifier.jsq1 support [\#856](https://github.com/rytilahti/python-miio/pull/856) ([syssi](https://github.com/syssi))
- Fix CLI of the PTC support \(dmaker.airfresh.t2017\) [\#855](https://github.com/rytilahti/python-miio/pull/855) ([syssi](https://github.com/syssi))
- Fix payload of all dmaker.airfresh.t2017 toggles [\#854](https://github.com/rytilahti/python-miio/pull/854) ([syssi](https://github.com/syssi))
- Fix fan speed property of the dmaker.fan.p11 [\#852](https://github.com/rytilahti/python-miio/pull/852) ([iquix](https://github.com/iquix))
- Initial support for lumi.curtain.hagl05 [\#851](https://github.com/rytilahti/python-miio/pull/851) ([in7egral](https://github.com/in7egral))
- Add basic dmaker.fan.p11 support [\#850](https://github.com/rytilahti/python-miio/pull/850) ([syssi](https://github.com/syssi))
- Vacuum: Implement TUI for the manual mode [\#845](https://github.com/rytilahti/python-miio/pull/845) ([rnovatorov](https://github.com/rnovatorov))
- Throwing GatewayException in get\_illumination [\#831](https://github.com/rytilahti/python-miio/pull/831) ([javicalle](https://github.com/javicalle))
- improve poetry usage documentation [\#830](https://github.com/rytilahti/python-miio/pull/830) ([rytilahti](https://github.com/rytilahti))
- Correct importlib\_metadata python\_version bounds [\#828](https://github.com/rytilahti/python-miio/pull/828) ([jonringer](https://github.com/jonringer))
- Remove \_\_json\_\_ boilerplate code from all status containers [\#827](https://github.com/rytilahti/python-miio/pull/827) ([rytilahti](https://github.com/rytilahti))
- Add basic support for yunmi.waterpuri.lx9 and lx11 [\#826](https://github.com/rytilahti/python-miio/pull/826) ([zhangjingye03](https://github.com/zhangjingye03))
- Add basic support for xiaomi.aircondition.mc1, mc2, mc4, mc5 [\#825](https://github.com/rytilahti/python-miio/pull/825) ([zhangjingye03](https://github.com/zhangjingye03))
- Bump cryptography dependency to new major version [\#824](https://github.com/rytilahti/python-miio/pull/824) ([rytilahti](https://github.com/rytilahti))
- Add support for dmaker.fan.p9 and dmaker.fan.p10 [\#819](https://github.com/rytilahti/python-miio/pull/819) ([swim2sun](https://github.com/swim2sun))
- Add support for lumi.acpartner.mcn02 [\#809](https://github.com/rytilahti/python-miio/pull/809) ([EugeneLiu](https://github.com/EugeneLiu))
- Add consumable status to viomi vacuum [\#805](https://github.com/rytilahti/python-miio/pull/805) ([titilambert](https://github.com/titilambert))
- Add zhimi.airfresh.va4 support [\#795](https://github.com/rytilahti/python-miio/pull/795) ([syssi](https://github.com/syssi))
- Fix zhimi.airfresh.va2 temperature [\#794](https://github.com/rytilahti/python-miio/pull/794) ([syssi](https://github.com/syssi))
- Make EnumType default to incasesensitive for cli tool [\#790](https://github.com/rytilahti/python-miio/pull/790) ([rytilahti](https://github.com/rytilahti))
- Rename Mopping to VacuumingAndMopping [\#785](https://github.com/rytilahti/python-miio/pull/785) ([rytilahti](https://github.com/rytilahti))
- Loosen pinned versions [\#781](https://github.com/rytilahti/python-miio/pull/781) ([rytilahti](https://github.com/rytilahti))
- Improve documentation presentation [\#777](https://github.com/rytilahti/python-miio/pull/777) ([rytilahti](https://github.com/rytilahti))
- Move raw\_id from Vacuum to the Device base class [\#776](https://github.com/rytilahti/python-miio/pull/776) ([rytilahti](https://github.com/rytilahti))


## [0.5.3](https://github.com/rytilahti/python-miio/tree/0.5.3) (2020-07-27)

New devices:
* Xiaomi Mi Air Humidifier CA4 (zhimi.humidifier.ca4) (@Toxblh)

Improvements:
* S5 vacuum: adjustable water volume for mopping
* Gateway: improved light controls (@starkillerOG)
* Chuangmi Camera: improved home monitoring support (@impankratov)

Fixes:
* Xioawa E25: do not crash when trying to access timers
* Vacuum: allow resuming after error in zoned cleanup (@r4nd0mbr1ck)


[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.5.2.1...0.5.3)

**Implemented enhancements:**

- Vacuum: Add water volume setting \(s5 max\) [\#773](https://github.com/rytilahti/python-miio/pull/773) ([rytilahti](https://github.com/rytilahti))
- improve gateway light class [\#770](https://github.com/rytilahti/python-miio/pull/770) ([starkillerOG](https://github.com/starkillerOG))

**Fixed bugs:**

- AqaraSmartBulbE27 support added in \#729 is not work [\#771](https://github.com/rytilahti/python-miio/issues/771)
- Broken timezone call \(dictionary instead of string\) breaks HASS integration [\#759](https://github.com/rytilahti/python-miio/issues/759)

**Closed issues:**

- Roborock S5 Max, Failure to connect in Homeassistant. [\#758](https://github.com/rytilahti/python-miio/issues/758)
- Unable to decrypt, returning raw bytes: b'' - while mirobo discovery [\#752](https://github.com/rytilahti/python-miio/issues/752)
- Error with Windows x64 python [\#733](https://github.com/rytilahti/python-miio/issues/733)
- Xiaomi Vacuum - resume clean-up after pause [\#471](https://github.com/rytilahti/python-miio/issues/471)

**Merged pull requests:**

- Remove labeler as it doesn't work as expected [\#774](https://github.com/rytilahti/python-miio/pull/774) ([rytilahti](https://github.com/rytilahti))
- Add support for zhimi.humidifier.ca4 \(miot\) [\#772](https://github.com/rytilahti/python-miio/pull/772) ([Toxblh](https://github.com/Toxblh))
- add "lumi.acpartner.v3" since it also works with this code [\#769](https://github.com/rytilahti/python-miio/pull/769) ([starkillerOG](https://github.com/starkillerOG))
- Add automatic labeling for PRs [\#768](https://github.com/rytilahti/python-miio/pull/768) ([rytilahti](https://github.com/rytilahti))
- Add --version to miiocli [\#767](https://github.com/rytilahti/python-miio/pull/767) ([rytilahti](https://github.com/rytilahti))
- Add preliminary issue templates [\#766](https://github.com/rytilahti/python-miio/pull/766) ([rytilahti](https://github.com/rytilahti))
- Create separate API doc pages per module [\#765](https://github.com/rytilahti/python-miio/pull/765) ([rytilahti](https://github.com/rytilahti))
- Add sphinxcontrib.apidoc to doc builds to keep the API index up-to-date [\#764](https://github.com/rytilahti/python-miio/pull/764) ([rytilahti](https://github.com/rytilahti))
- Resume zoned clean from error state [\#763](https://github.com/rytilahti/python-miio/pull/763) ([r4nd0mbr1ck](https://github.com/r4nd0mbr1ck))
- Allow alternative timezone format seen in Xioawa E25 [\#760](https://github.com/rytilahti/python-miio/pull/760) ([rytilahti](https://github.com/rytilahti))
- Fix readthedocs build after poetry convert [\#755](https://github.com/rytilahti/python-miio/pull/755) ([rytilahti](https://github.com/rytilahti))
- Add retries to discovery requests [\#754](https://github.com/rytilahti/python-miio/pull/754) ([rytilahti](https://github.com/rytilahti))
- AirPurifier MIoT: round temperature  [\#753](https://github.com/rytilahti/python-miio/pull/753) ([petrkotek](https://github.com/petrkotek))
- chuangmi\_camera: Improve home monitoring support [\#751](https://github.com/rytilahti/python-miio/pull/751) ([impankratov](https://github.com/impankratov))


## [0.5.2.1](https://github.com/rytilahti/python-miio/tree/0.5.2.1) (2020-07-03)

A quick minor fix for vacuum gen1 fan speed detection.

[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.5.2...0.5.2.1)

**Merged pull requests:**

- vacuum: Catch DeviceInfoUnavailableException for model detection [\#748](https://github.com/rytilahti/python-miio/pull/748) ([rytilahti](https://github.com/rytilahti))

## [0.5.2](https://github.com/rytilahti/python-miio/tree/0.5.2) (2020-07-03)

This release brings several improvements to the gateway support, thanks to @starkillerOG as well as some minor improvements and fixes to some other parts.

Improvements:
* gateway: plug controls, support for aqara wall outlet and aqara smart bulbs, ability to enable telnet access & general improvements
* viomi: ability to change the mopping pattern
* fan: ability to disable delayed turn off

Fixes:
* airpurifier_miot: Incorrect get_properties usage


[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.5.1...0.5.2)

**Fixed bugs:**

- Air priefier H3 doasn't work in 0.5.1 [\#730](https://github.com/rytilahti/python-miio/issues/730)

**Closed issues:**

- Viomi V8: AttributeError: 'NoneType' object has no attribute 'header' [\#746](https://github.com/rytilahti/python-miio/issues/746)
- viomi: add command for changing the mopping mode [\#725](https://github.com/rytilahti/python-miio/issues/725)
- fan za3, got token, but does not work [\#720](https://github.com/rytilahti/python-miio/issues/720)
- Capitalisation of Air Purifier modes [\#715](https://github.com/rytilahti/python-miio/issues/715)
- STYJ02YM Unable to decrypt error [\#701](https://github.com/rytilahti/python-miio/issues/701)

**Merged pull requests:**

- Use "get\_properties" instead of "get\_prop" for miot devices [\#745](https://github.com/rytilahti/python-miio/pull/745) ([rytilahti](https://github.com/rytilahti))
- viomi: add ability to change the mopping pattern [\#744](https://github.com/rytilahti/python-miio/pull/744) ([rytilahti](https://github.com/rytilahti))
- fan: Ability to disable delayed turn off functionality [\#741](https://github.com/rytilahti/python-miio/pull/741) ([insajd](https://github.com/insajd))
- Gateway: Add control commands to Plug [\#737](https://github.com/rytilahti/python-miio/pull/737) ([starkillerOG](https://github.com/starkillerOG))
- gateway: cleanup SensorHT and Plug class [\#735](https://github.com/rytilahti/python-miio/pull/735) ([starkillerOG](https://github.com/starkillerOG))
- Add "enable\_telnet" to gateway [\#734](https://github.com/rytilahti/python-miio/pull/734) ([starkillerOG](https://github.com/starkillerOG))
- prevent errors on "lumi.gateway.mieu01" [\#732](https://github.com/rytilahti/python-miio/pull/732) ([starkillerOG](https://github.com/starkillerOG))
- Moved access to discover message attribute inside 'if message is not None' statement [\#731](https://github.com/rytilahti/python-miio/pull/731) ([jthure](https://github.com/jthure))
- Add AqaraSmartBulbE27 support [\#729](https://github.com/rytilahti/python-miio/pull/729) ([starkillerOG](https://github.com/starkillerOG))
- Gateway: add name + model property to subdevice & add loads of subdevices [\#724](https://github.com/rytilahti/python-miio/pull/724) ([starkillerOG](https://github.com/starkillerOG))
- Add gentle mode for Roborock E2 [\#723](https://github.com/rytilahti/python-miio/pull/723) ([tribut](https://github.com/tribut))
- gateway: add model property & implement SwitchOneChannel [\#722](https://github.com/rytilahti/python-miio/pull/722) ([starkillerOG](https://github.com/starkillerOG))
- Add support for fanspeeds of Roborock E2 \(E20/E25\) [\#718](https://github.com/rytilahti/python-miio/pull/718) ([tribut](https://github.com/tribut))
- add AqaraWallOutlet support [\#717](https://github.com/rytilahti/python-miio/pull/717) ([starkillerOG](https://github.com/starkillerOG))
- Add new device type mappings, add note about 'used\_for\_public' [\#713](https://github.com/rytilahti/python-miio/pull/713) ([starkillerOG](https://github.com/starkillerOG))

## [0.5.1](https://github.com/rytilahti/python-miio/tree/0.5.1) (2020-06-04)

The most noteworthy change in this release is the work undertaken by @starkillerOG to improve the support for Xiaomi gateway devices. See the PR description for more details at https://github.com/rytilahti/python-miio/pull/700 .

For downstream developers, this release adds two new exceptions to allow better control in situations where the response payloads from the device are something unexpected. This is useful for gracefully fallbacks when automatic device type discovery fails.

P.S. There is now a matrix room (https://matrix.to/#/#python-miio-chat:matrix.org) so feel free to hop in for any reason.

This release adds support for the following new devices:

* chuangmi.plug.hmi208
* Gateway subdevices: Aqara Wireless Relay 2ch (@bskaplou), AqaraSwitch{One,Two}Channels (@starkillerOG)

Fixes & Enhancements:

* The initial UDP handshake is sent now several times to accommodate spotty networks
* chuangmi.camera.ipc019: camera rotation & alarm activation
* Vacuum: added next_schedule property for timers, water tank status, is_on state for segment cleaning mode
* chuangmi.plug.v3: works now with updated firmware version
* Viomi vacuum: various minor fixes

API changes:

* Device.send() accepts `extra_parameters` to allow passing values to the main payload body. This is useful at least for gateway devices.

* Two new exceptions to give more control to downstream developers:
  * PayloadDecodeException (when the payload is unparseable)
  * DeviceInfoUnavailableException (when device.info() fails)
* Dependency management is now done using poetry & pyproject.toml


[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.5.0.1...0.5.1)

**Implemented enhancements:**

- How to enhance the Xiaomi camera\(chuangmi.camera.ipc019\) function [\#655](https://github.com/rytilahti/python-miio/issues/655)
- miio local api soon deprecated? / add support for miot api [\#543](https://github.com/rytilahti/python-miio/issues/543)

**Fixed bugs:**

- STYJ02YM - AttributeError: 'ViomiVacuumStatus' object has no attribute 'mop\_type' [\#704](https://github.com/rytilahti/python-miio/issues/704)
- 0.5.0 / 0.5.0.1 breaks viomivacuum status [\#694](https://github.com/rytilahti/python-miio/issues/694)
- Error controlling gateway [\#673](https://github.com/rytilahti/python-miio/issues/673)

**Closed issues:**

- xiaomi fan 1x  encountered  'user ack timeout' [\#714](https://github.com/rytilahti/python-miio/issues/714)
- New device it's possible ? Ikea tradfri GU10 [\#707](https://github.com/rytilahti/python-miio/issues/707)
- not supported chuangmi.plug.hmi208 [\#691](https://github.com/rytilahti/python-miio/issues/691)
- `is\_on` not correct [\#687](https://github.com/rytilahti/python-miio/issues/687)
- Enhancement request: get snapshot / recording from chuangmi camera [\#682](https://github.com/rytilahti/python-miio/issues/682)
- Add support to Xiaomi Mi Home 360 1080p MJSXJ05CM  [\#671](https://github.com/rytilahti/python-miio/issues/671)
- Xiaomi Mi Air Purifier 3H \(zhimi-airpurifier-mb3\)  [\#670](https://github.com/rytilahti/python-miio/issues/670)
- Can't connect to vacuum anymore [\#667](https://github.com/rytilahti/python-miio/issues/667)
- error timeout - adding supported to viomi-vacuum-v8\_miio 309248236  [\#666](https://github.com/rytilahti/python-miio/issues/666)
- python-miio v0.5.0 incomplete utils.py [\#659](https://github.com/rytilahti/python-miio/issues/659)
- REQ: vacuum - restore map function ? [\#646](https://github.com/rytilahti/python-miio/issues/646)
- Unsupported device found - chuangmi.plug.hmi208 [\#616](https://github.com/rytilahti/python-miio/issues/616)
- Viomi V2 discoverable, not responding [\#597](https://github.com/rytilahti/python-miio/issues/597)

**Merged pull requests:**

- Add next\_schedule to vacuum timers [\#712](https://github.com/rytilahti/python-miio/pull/712) ([MarBra](https://github.com/MarBra))
- gateway: add support for AqaraSwitchOneChannel and AqaraSwitchTwoChannels [\#708](https://github.com/rytilahti/python-miio/pull/708) ([starkillerOG](https://github.com/starkillerOG))
- Viomi: Expose mop\_type, fix error string handling and fix water\_grade [\#705](https://github.com/rytilahti/python-miio/pull/705) ([rytilahti](https://github.com/rytilahti))
- restructure and improve gateway subdevices [\#700](https://github.com/rytilahti/python-miio/pull/700) ([starkillerOG](https://github.com/starkillerOG))
- Added support of Aqara Wireless Relay 2ch \(LLKZMK11LM\) [\#696](https://github.com/rytilahti/python-miio/pull/696) ([bskaplou](https://github.com/bskaplou))
- Viomi: Use bin\_type instead of box\_type for cli tool [\#695](https://github.com/rytilahti/python-miio/pull/695) ([rytilahti](https://github.com/rytilahti))
- Add support for chuangmi.plug.hmi208 [\#693](https://github.com/rytilahti/python-miio/pull/693) ([rytilahti](https://github.com/rytilahti))
- vacuum: is\_on should be true for segment cleaning [\#688](https://github.com/rytilahti/python-miio/pull/688) ([rytilahti](https://github.com/rytilahti))
- send multiple handshake requests [\#686](https://github.com/rytilahti/python-miio/pull/686) ([rytilahti](https://github.com/rytilahti))
- Add PayloadDecodeException and DeviceInfoUnavailableException [\#685](https://github.com/rytilahti/python-miio/pull/685) ([rytilahti](https://github.com/rytilahti))
- update readme \(matrix room, usage instructions\) [\#684](https://github.com/rytilahti/python-miio/pull/684) ([rytilahti](https://github.com/rytilahti))
- Fix Gateway constructor to follow baseclass' parameters [\#677](https://github.com/rytilahti/python-miio/pull/677) ([rytilahti](https://github.com/rytilahti))
- Update vacuum doc to actual lib output [\#676](https://github.com/rytilahti/python-miio/pull/676) ([ckesc](https://github.com/ckesc))
- Xiaomi vacuum. Add property for water box \(water tank\) attach status [\#675](https://github.com/rytilahti/python-miio/pull/675) ([ckesc](https://github.com/ckesc))
- Convert to use pyproject.toml and poetry, extend tests to more platforms [\#674](https://github.com/rytilahti/python-miio/pull/674) ([rytilahti](https://github.com/rytilahti))
- add viomi.vacuum.v8 to discovery [\#668](https://github.com/rytilahti/python-miio/pull/668) ([rytilahti](https://github.com/rytilahti))
- chuangmi.plug.v3: Fixed power state status for updated firmware [\#665](https://github.com/rytilahti/python-miio/pull/665) ([ad](https://github.com/ad))
- Xiaomi camera \(chuangmi.camera.ipc019\): Add orientation controls and alarm [\#663](https://github.com/rytilahti/python-miio/pull/663) ([rytilahti](https://github.com/rytilahti))
- Add Device.get\_properties\(\), cleanup devices using get\_prop [\#657](https://github.com/rytilahti/python-miio/pull/657) ([rytilahti](https://github.com/rytilahti))
- Add extra\_parameters to send\(\) [\#653](https://github.com/rytilahti/python-miio/pull/653) ([rytilahti](https://github.com/rytilahti))

## [0.5.0.1](https://github.com/rytilahti/python-miio/tree/0.5.0.1)

Due to a mistake during the release process, some changes were completely left out from the release.
This release simply bases itself on the current master to fix that.

[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.5.0...0.5.0.1)

**Closed issues:**

- Xiaomi Mijia Smart Sterilization Humidifier \(SCK0A45\) error - DEBUG:miio.protocol:Unable to decrypt, returning raw bytes: b'' [\#649](https://github.com/rytilahti/python-miio/issues/649)

**Merged pull requests:**

- Prepare for 0.5.0 [\#658](https://github.com/rytilahti/python-miio/pull/658) ([rytilahti](https://github.com/rytilahti))
- Add miottemplate tool to simplify adding support for new miot devices [\#656](https://github.com/rytilahti/python-miio/pull/656) ([rytilahti](https://github.com/rytilahti))
- Add Xiaomi Zero Fog Humidifier \(shuii.humidifier.jsq001\) support \(\#642\) [\#654](https://github.com/rytilahti/python-miio/pull/654) ([iromeo](https://github.com/iromeo))
- Gateway get\_device\_prop\_exp command [\#652](https://github.com/rytilahti/python-miio/pull/652) ([fsalomon](https://github.com/fsalomon))
- Add fan\_speed\_presets\(\) for querying available fan speeds [\#643](https://github.com/rytilahti/python-miio/pull/643) ([rytilahti](https://github.com/rytilahti))
- Initial support for xiaomi gateway devices [\#470](https://github.com/rytilahti/python-miio/pull/470) ([rytilahti](https://github.com/rytilahti))


## [0.5.0](https://github.com/rytilahti/python-miio/tree/0.5.0)

Xiaomi is slowly moving to use new protocol dubbed MiOT on the newer devices. To celebrate the integration of initial support for this protocol, it is time to jump from 0.4 to 0.5 series! Shout-out to @rezmus for the insightful notes, links, clarifications on #543 to help to understand how the protocol works!

Special thanks go to both @petrkotek (for initial support) and @foxel (for polishing it for this release) for making this possible. The ground work they did will make adding support for other new miot devices possible.

For those who are interested in adding support to new MiOT devices can check out devtools directory in the git repository, which now hosts a tool to simplify the process. As always, contributions are  welcome!

This release adds support for the following new devices:
* Air purifier 3/3H support (zhimi.airpurifier.mb3, zhimi.airpurifier.ma4)
* Xiaomi Gateway devices (lumi.gateway.v3, basic support)
* SmartMi Zhimi Heaters (zhimi.heater.za2)
* Xiaomi Zero Fog Humidifier (shuii.humidifier.jsq001)

Fixes & Enhancements:
* Vacuum objects can now be queried for supported fanspeeds
* Several improvements to Viomi vacuums
* Roborock S6: recovery map controls
* And some other fixes, see the full changelog!

[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.4.8...0.5.0)

**Closed issues:**

- viomi.vacuum.v7 and zhimi.airpurifier.mb3 support homeassistain yet? [\#645](https://github.com/rytilahti/python-miio/issues/645)
- subcon should be a Construct field [\#641](https://github.com/rytilahti/python-miio/issues/641)
- Roborock S6 - only reachable from different subnet [\#640](https://github.com/rytilahti/python-miio/issues/640)
- Python 3.7 error [\#639](https://github.com/rytilahti/python-miio/issues/639)
- Posibillity for local push instead of poll? [\#638](https://github.com/rytilahti/python-miio/issues/638)
- Xiaomi STYJ02YM discovered but not responding [\#628](https://github.com/rytilahti/python-miio/issues/628)
- miplug module is not working from python scrips [\#621](https://github.com/rytilahti/python-miio/issues/621)
- Unsupported device found: zhimi.humidifier.v1 [\#620](https://github.com/rytilahti/python-miio/issues/620)
- Support for Smartmi Radiant Heater Smart Version \(zhimi.heater.za2\) [\#615](https://github.com/rytilahti/python-miio/issues/615)
- Support for Xiaomi Qingping Bluetooth Alarm Clock? [\#614](https://github.com/rytilahti/python-miio/issues/614)
- How to connect a device to WIFI without MiHome app  |  Can I connect a device to WIFI using Raspberry Pi?  \#help wanted \#Support [\#609](https://github.com/rytilahti/python-miio/issues/609)
- Additional commands for vacuum [\#607](https://github.com/rytilahti/python-miio/issues/607)
- "cgllc.airmonitor.b1"   No response from the device [\#603](https://github.com/rytilahti/python-miio/issues/603)
- Xiao AI Smart Alarm Clock Time [\#600](https://github.com/rytilahti/python-miio/issues/600)
- Support new device \(yeelink.light.lamp4\) [\#598](https://github.com/rytilahti/python-miio/issues/598)
- Errors not shown for S6 [\#595](https://github.com/rytilahti/python-miio/issues/595)
- Fully charged state not shown [\#594](https://github.com/rytilahti/python-miio/issues/594)
- Support for Roborock S6/T6 [\#593](https://github.com/rytilahti/python-miio/issues/593)
- Pi3 b python error [\#588](https://github.com/rytilahti/python-miio/issues/588)
- Support for Xiaomi Air Purifier 3 \(zhimi.airpurifier.ma4\) [\#577](https://github.com/rytilahti/python-miio/issues/577)
- Updater: Uses wrong local IP address for HTTP server [\#571](https://github.com/rytilahti/python-miio/issues/571)
- How to deal with getDeviceWifi\(\).subscribe [\#528](https://github.com/rytilahti/python-miio/issues/528)
- Move Roborock when in error [\#524](https://github.com/rytilahti/python-miio/issues/524)
- Roborock v2 zoned\_clean\(\) doesn't work [\#490](https://github.com/rytilahti/python-miio/issues/490)
- \[ADD\] Xiaomi Mijia Caméra IP WiFi 1080P Panoramique [\#484](https://github.com/rytilahti/python-miio/issues/484)
- Add unit tests [\#88](https://github.com/rytilahti/python-miio/issues/88)
- Get the map from Mi Vacuum V1? [\#356](https://github.com/rytilahti/python-miio/issues/356)

**Merged pull requests:**

- Add miottemplate tool to simplify adding support for new miot devices [\#656](https://github.com/rytilahti/python-miio/pull/656) ([rytilahti](https://github.com/rytilahti))
- Add Xiaomi Zero Fog Humidifier \(shuii.humidifier.jsq001\) support \(\#642\) [\#654](https://github.com/rytilahti/python-miio/pull/654) ([iromeo](https://github.com/iromeo))
- Gateway get\_device\_prop\_exp command [\#652](https://github.com/rytilahti/python-miio/pull/652) ([fsalomon](https://github.com/fsalomon))
- Add fan\_speed\_presets\(\) for querying available fan speeds [\#643](https://github.com/rytilahti/python-miio/pull/643) ([rytilahti](https://github.com/rytilahti))
- Air purifier 3/3H support \(remastered\) [\#634](https://github.com/rytilahti/python-miio/pull/634) ([foxel](https://github.com/foxel))
- Add eyecare on/off to philips\_eyecare\_cli [\#631](https://github.com/rytilahti/python-miio/pull/631) ([hhrsscc](https://github.com/hhrsscc))
- Extend viomi vacuum support [\#626](https://github.com/rytilahti/python-miio/pull/626) ([rytilahti](https://github.com/rytilahti))
- Add support for SmartMi Zhimi Heaters [\#625](https://github.com/rytilahti/python-miio/pull/625) ([bazuchan](https://github.com/bazuchan))
- Add error code 24 definition \("No-go zone or invisible wall detected"\) [\#623](https://github.com/rytilahti/python-miio/pull/623) ([insajd](https://github.com/insajd))
- s6: two new commands for map handling [\#608](https://github.com/rytilahti/python-miio/pull/608) ([glompfine](https://github.com/glompfine))
- Refactoring: Split Device class into Device+Protocol [\#592](https://github.com/rytilahti/python-miio/pull/592) ([petrkotek](https://github.com/petrkotek))
- STYJ02YM: Manual movement and mop mode support [\#590](https://github.com/rytilahti/python-miio/pull/590) ([rumpeltux](https://github.com/rumpeltux))
- Initial support for xiaomi gateway devices [\#470](https://github.com/rytilahti/python-miio/pull/470) ([rytilahti](https://github.com/rytilahti))


## [0.4.8](https://github.com/rytilahti/python-miio/tree/0.4.8)

This release adds support for the following new devices:

* Xiaomi Mijia STYJ02YM vacuum \(viomi.vacuum.v7\)
* Xiaomi Mi Smart Humidifier \(deerma.humidifier.mjjsq\)
* Xiaomi Mi Fresh Air Ventilator \(dmaker.airfresh.t2017\)
* Xiaomi Philips Desk Lamp RW Read \(philips.light.rwread\)
* Xiaomi Philips LED Ball Lamp White \(philips.light.hbulb\)

Fixes & Enhancements:

* Improve Xiaomi Tinymu Smart Toilet Cover support
* Remove UTF-8 encoding definition from source files
* Azure pipeline for tests
* Pre-commit hook to enforce black, flake8 and isort
* Pre-commit hook to check-manifest, check for pypi-description, flake8-docstrings

[Full Changelog](https://github.com/rytilahti/python-miio/compare/0.4.7...0.4.8)

**Implemented enhancements:**

- Support for new vaccum Xiaomi Mijia STYJ02YM  [\#550](https://github.com/rytilahti/python-miio/issues/550)
- Support for Mi Smart Humidifier \(deerma.humidifier.mjjsq\) [\#533](https://github.com/rytilahti/python-miio/issues/533)
- Support for Mi Fresh Air Ventilator dmaker.airfresh.t2017 [\#502](https://github.com/rytilahti/python-miio/issues/502)

**Closed issues:**

- The voice pack does not change in Xiaomi Vacuum 1S [\#583](https://github.com/rytilahti/python-miio/issues/583)
- Support for chuangmi.plug.hmi206 [\#574](https://github.com/rytilahti/python-miio/issues/574)
- miplug crash in macos catalina 10.15.1 [\#573](https://github.com/rytilahti/python-miio/issues/573)
- Roborock S50 not responding to handshake anymore [\#572](https://github.com/rytilahti/python-miio/issues/572)
- Cannot control my Roborock S50 through my home wifi network [\#570](https://github.com/rytilahti/python-miio/issues/570)
- I can not get load\_power with my set is Xiaomi Smart WiFi with two usb \(chuangmi.plug.v3\) [\#549](https://github.com/rytilahti/python-miio/issues/549)

**Merged pull requests:**

- Add Xiaomi Mi Fresh Air \(dmaker.airfresh.t2017\) support [\#591](https://github.com/rytilahti/python-miio/pull/591) ([syssi](https://github.com/syssi))
- Add philips.light.rwread support [\#589](https://github.com/rytilahti/python-miio/pull/589) ([syssi](https://github.com/syssi))
- Add philips.light.hbulb support [\#587](https://github.com/rytilahti/python-miio/pull/587) ([syssi](https://github.com/syssi))
- Add support for deerma.humidifier.mjjsq [\#586](https://github.com/rytilahti/python-miio/pull/586) ([syssi](https://github.com/syssi))
- Improve toiletlid various parameters [\#579](https://github.com/rytilahti/python-miio/pull/579) ([scp10011](https://github.com/scp10011))
- Add support for Xiaomi Mijia STYJ02YM \(viomi.vacuum.v7\) [\#576](https://github.com/rytilahti/python-miio/pull/576) ([rytilahti](https://github.com/rytilahti))
- Add check-manifest, check for pypi-description, flake8-docstrings [\#575](https://github.com/rytilahti/python-miio/pull/575) ([rytilahti](https://github.com/rytilahti))
- Remove UTF-8 encoding comment [\#569](https://github.com/rytilahti/python-miio/pull/569) ([quamilek](https://github.com/quamilek))
- Improve the contribution process with better checks and docs [\#568](https://github.com/rytilahti/python-miio/pull/568) ([rytilahti](https://github.com/rytilahti))
- add azure pipeline for tests, and enforce black, flake8 and isort for commits [\#566](https://github.com/rytilahti/python-miio/pull/566) ([rytilahti](https://github.com/rytilahti))

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
