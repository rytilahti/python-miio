import codecs
import inspect
import logging
import time
from functools import partial
from ipaddress import ip_address
from typing import Callable, Dict, Optional, Type, Union  # noqa: F401

import zeroconf

from miio.integrations.airpurifier import (
    AirDogX3,
    AirFresh,
    AirFreshT2017,
    AirPurifier,
    AirPurifierMiot,
)
from miio.integrations.humidifier import (
    AirHumidifier,
    AirHumidifierJsq,
    AirHumidifierJsqs,
    AirHumidifierMjjsq,
)
from miio.integrations.vacuum import DreameVacuum, RoborockVacuum, ViomiVacuum

from . import (
    AirConditionerMiot,
    AirConditioningCompanion,
    AirConditioningCompanionMcn02,
    AirQualityMonitor,
    AqaraCamera,
    Ceil,
    ChuangmiCamera,
    ChuangmiIr,
    ChuangmiPlug,
    Cooker,
    Device,
    Gateway,
    Heater,
    PowerStrip,
    Toiletlid,
    WaterPurifier,
    WaterPurifierYunmi,
    WifiRepeater,
    WifiSpeaker,
)
from .airconditioningcompanion import (
    MODEL_ACPARTNER_V1,
    MODEL_ACPARTNER_V2,
    MODEL_ACPARTNER_V3,
)
from .airconditioningcompanionMCN import MODEL_ACPARTNER_MCN02
from .airqualitymonitor import (
    MODEL_AIRQUALITYMONITOR_B1,
    MODEL_AIRQUALITYMONITOR_S1,
    MODEL_AIRQUALITYMONITOR_V1,
)
from .alarmclock import AlarmClock
from .chuangmi_plug import (
    MODEL_CHUANGMI_PLUG_HMI205,
    MODEL_CHUANGMI_PLUG_HMI206,
    MODEL_CHUANGMI_PLUG_M1,
    MODEL_CHUANGMI_PLUG_M3,
    MODEL_CHUANGMI_PLUG_V1,
    MODEL_CHUANGMI_PLUG_V2,
    MODEL_CHUANGMI_PLUG_V3,
)
from .heater import MODEL_HEATER_MA1, MODEL_HEATER_ZA1
from .integrations.fan import Fan, FanLeshow, FanMiot, FanZA5
from .integrations.light import (
    PhilipsBulb,
    PhilipsEyecare,
    PhilipsMoonlight,
    PhilipsRwread,
    PhilipsWhiteBulb,
    Yeelight,
)
from .powerstrip import MODEL_POWER_STRIP_V1, MODEL_POWER_STRIP_V2
from .toiletlid import MODEL_TOILETLID_V1

_LOGGER = logging.getLogger(__name__)


DEVICE_MAP: Dict[str, Union[Type[Device], partial]] = {
    "rockrobo-vacuum-v1": RoborockVacuum,
    "roborock-vacuum-s5": RoborockVacuum,
    "roborock-vacuum-m1s": RoborockVacuum,
    "roborock-vacuum-a10": RoborockVacuum,
    "chuangmi-plug-m1": partial(ChuangmiPlug, model=MODEL_CHUANGMI_PLUG_M1),
    "chuangmi-plug-m3": partial(ChuangmiPlug, model=MODEL_CHUANGMI_PLUG_M3),
    "chuangmi-plug-v1": partial(ChuangmiPlug, model=MODEL_CHUANGMI_PLUG_V1),
    "chuangmi-plug-v2": partial(ChuangmiPlug, model=MODEL_CHUANGMI_PLUG_V2),
    "chuangmi-plug-v3": partial(ChuangmiPlug, model=MODEL_CHUANGMI_PLUG_V3),
    "chuangmi-plug-hmi205": partial(ChuangmiPlug, model=MODEL_CHUANGMI_PLUG_HMI205),
    "chuangmi-plug-hmi206": partial(ChuangmiPlug, model=MODEL_CHUANGMI_PLUG_HMI206),
    "chuangmi-plug_": partial(ChuangmiPlug, model=MODEL_CHUANGMI_PLUG_V1),
    "qmi-powerstrip-v1": partial(PowerStrip, model=MODEL_POWER_STRIP_V1),
    "zimi-powerstrip-v2": partial(PowerStrip, model=MODEL_POWER_STRIP_V2),
    "zimi-clock-myk01": AlarmClock,
    "xiaomi.aircondition.mc1": AirConditionerMiot,
    "xiaomi.aircondition.mc2": AirConditionerMiot,
    "xiaomi.aircondition.mc4": AirConditionerMiot,
    "xiaomi.aircondition.mc5": AirConditionerMiot,
    "airdog-airpurifier-x3": AirDogX3,
    "airdog-airpurifier-x5": AirDogX3,
    "airdog-airpurifier-x7sm": AirDogX3,
    "zhimi-airpurifier-m1": AirPurifier,  # mini model
    "zhimi-airpurifier-m2": AirPurifier,  # mini model 2
    "zhimi-airpurifier-ma1": AirPurifier,  # ms model
    "zhimi-airpurifier-ma2": AirPurifier,  # ms model 2
    "zhimi-airpurifier-sa1": AirPurifier,  # super model
    "zhimi-airpurifier-sa2": AirPurifier,  # super model 2
    "zhimi-airpurifier-v1": AirPurifier,  # v1
    "zhimi-airpurifier-v2": AirPurifier,  # v2
    "zhimi-airpurifier-v3": AirPurifier,  # v3
    "zhimi-airpurifier-v5": AirPurifier,  # v5
    "zhimi-airpurifier-v6": AirPurifier,  # v6
    "zhimi-airpurifier-v7": AirPurifier,  # v7
    "zhimi-airpurifier-mc1": AirPurifier,  # mc1
    "zhimi-airpurifier-mb3": AirPurifierMiot,  # mb3 (3/3H)
    "zhimi-airpurifier-ma4": AirPurifierMiot,  # ma4 (3)
    "zhimi-airpurifier-vb2": AirPurifierMiot,  # vb2 (Pro H)
    "chuangmi-camera-ipc009": ChuangmiCamera,
    "chuangmi-camera-ipc019": ChuangmiCamera,
    "chuangmi-ir-v2": ChuangmiIr,
    "chuangmi-remote-h102a03_": ChuangmiIr,
    "zhimi-humidifier-v1": AirHumidifier,
    "zhimi-humidifier-ca1": AirHumidifier,
    "zhimi-humidifier-cb1": AirHumidifier,
    "shuii-humidifier-jsq001": AirHumidifierJsq,
    "deerma-humidifier-mjjsq": AirHumidifierMjjsq,
    "deerma-humidifier-jsq1": AirHumidifierMjjsq,
    "deerma-humidifier-jsqs": AirHumidifierJsqs,
    "yunmi-waterpuri-v2": WaterPurifier,
    "yunmi.waterpuri.lx9": WaterPurifierYunmi,
    "yunmi.waterpuri.lx11": WaterPurifierYunmi,
    "philips-light-bulb": PhilipsBulb,  # cannot be discovered via mdns
    "philips-light-hbulb": PhilipsWhiteBulb,  # cannot be discovered via mdns
    "philips-light-candle": PhilipsBulb,  # cannot be discovered via mdns
    "philips-light-candle2": PhilipsBulb,  # cannot be discovered via mdns
    "philips-light-ceiling": Ceil,
    "philips-light-zyceiling": Ceil,
    "philips-light-sread1": PhilipsEyecare,  # name needs to be checked
    "philips-light-moonlight": PhilipsMoonlight,  # name needs to be checked
    "philips-light-rwread": PhilipsRwread,  # name needs to be checked
    "xiaomi-wifispeaker-v1": WifiSpeaker,  # name needs to be checked
    "xiaomi-repeater-v1": WifiRepeater,  # name needs to be checked
    "xiaomi-repeater-v3": WifiRepeater,  # name needs to be checked
    "chunmi-cooker-press1": Cooker,
    "chunmi-cooker-press2": Cooker,
    "chunmi-cooker-normal1": Cooker,
    "chunmi-cooker-normal2": Cooker,
    "chunmi-cooker-normal3": Cooker,
    "chunmi-cooker-normal4": Cooker,
    "chunmi-cooker-normal5": Cooker,
    "lumi-acpartner-v1": partial(AirConditioningCompanion, model=MODEL_ACPARTNER_V1),
    "lumi-acpartner-v2": partial(AirConditioningCompanion, model=MODEL_ACPARTNER_V2),
    "lumi-acpartner-v3": partial(AirConditioningCompanion, model=MODEL_ACPARTNER_V3),
    "lumi-acpartner-mcn02": partial(
        AirConditioningCompanionMcn02, model=MODEL_ACPARTNER_MCN02
    ),
    "lumi-camera-aq2": AqaraCamera,
    "yeelink-light-": Yeelight,
    "leshow-fan-ss4": FanLeshow,
    "zhimi-fan-v2": Fan,
    "zhimi-fan-v3": Fan,
    "zhimi-fan-sa1": Fan,
    "zhimi-fan-za1": Fan,
    "zhimi-fan-za3": Fan,
    "zhimi-fan-za4": Fan,
    "dmaker-fan-1c": FanMiot,
    "dmaker-fan-p5": Fan,
    "dmaker-fan-p9": FanMiot,
    "dmaker-fan-p10": FanMiot,
    "dmaker-fan-p11": FanMiot,
    "zhimi-fan-za5": FanZA5,
    "tinymu-toiletlid-v1": partial(Toiletlid, model=MODEL_TOILETLID_V1),
    "zhimi-airfresh-va2": AirFresh,
    "zhimi-airfresh-va4": AirFresh,
    "dmaker-airfresh-t2017": AirFreshT2017,
    "zhimi-airmonitor-v1": partial(AirQualityMonitor, model=MODEL_AIRQUALITYMONITOR_V1),
    "cgllc-airmonitor-b1": partial(AirQualityMonitor, model=MODEL_AIRQUALITYMONITOR_B1),
    "cgllc-airmonitor-s1": partial(AirQualityMonitor, model=MODEL_AIRQUALITYMONITOR_S1),
    "lumi-gateway-": Gateway,
    "viomi-vacuum-v7": ViomiVacuum,
    "viomi-vacuum-v8": ViomiVacuum,
    "zhimi.heater.za1": partial(Heater, model=MODEL_HEATER_ZA1),
    "zhimi.elecheater.ma1": partial(Heater, model=MODEL_HEATER_MA1),
    "dreame-vacuum-mc1808": DreameVacuum,
    "dreame-vacuum-p2008": DreameVacuum,
    "dreame-vacuum-p2028": DreameVacuum,
    "dreame-vacuum-p2009": DreameVacuum,
}


def pretty_token(token):
    """Return a pretty string presentation for a token."""
    return codecs.encode(token, "hex").decode()


def get_addr_from_info(info):
    addrs = info.addresses
    if len(addrs) > 1:
        _LOGGER.warning(
            "More than single IP address in the advertisement, using the first one"
        )

    return str(ip_address(addrs[0]))


def other_package_info(info, desc):
    """Return information about another package supporting the device."""
    return f"Found {info.name} at {get_addr_from_info(info)}, check {desc}"


def create_device(name: str, addr: str, device_cls: partial) -> Device:
    """Return a device object for a zeroconf entry."""
    _LOGGER.debug(
        "Found a supported '%s', using '%s' class", name, device_cls.func.__name__
    )

    dev = device_cls(ip=addr)
    m = dev.send_handshake()
    dev.token = m.checksum
    _LOGGER.info(
        "Found a supported '%s' at %s - token: %s",
        device_cls.func.__name__,
        addr,
        pretty_token(dev.token),
    )
    return dev


class Listener(zeroconf.ServiceListener):
    """mDNS listener creating Device objects based on detected devices."""

    def __init__(self):
        self.found_devices = {}  # type: Dict[str, Device]

    def check_and_create_device(self, info, addr) -> Optional[Device]:
        """Create a corresponding :class:`Device` implementation for a given info and
        address.."""
        name = info.name
        for identifier, v in DEVICE_MAP.items():
            if name.startswith(identifier):
                if inspect.isclass(v):
                    return create_device(name, addr, partial(v))
                elif isinstance(v, partial) and inspect.isclass(v.func):
                    return create_device(name, addr, v)
                elif callable(v):
                    dev = Device(ip=addr)
                    _LOGGER.info(
                        "%s: token: %s",
                        v(info),
                        pretty_token(dev.send_handshake().checksum),
                    )
                    return None
        _LOGGER.warning(
            "Found unsupported device %s at %s, " "please report to developers",
            name,
            addr,
        )
        return None

    def add_service(self, zeroconf: "zeroconf.Zeroconf", type_: str, name: str) -> None:
        """Callback for discovery responses."""
        info = zeroconf.get_service_info(type_, name)
        addr = get_addr_from_info(info)

        if addr not in self.found_devices:
            dev = self.check_and_create_device(info, addr)
            if dev is not None:
                self.found_devices[addr] = dev

    def update_service(self, zc: "zeroconf.Zeroconf", type_: str, name: str) -> None:
        """Callback for state updates, which we ignore for now."""


class Discovery:
    """mDNS discoverer for miIO based devices (_miio._udp.local).

    Calling :func:`discover_mdns` will cause this to subscribe for updates on
    ``_miio._udp.local`` until any key is pressed, after which a dict of detected
    devices is returned.
    """

    @staticmethod
    def discover_mdns(*, timeout=5) -> Dict[str, Device]:
        """Discover devices with mdns until any keyboard input."""
        _LOGGER.info("Discovering devices with mDNS for %s seconds...", timeout)

        listener = Listener()
        browser = zeroconf.ServiceBrowser(
            zeroconf.Zeroconf(), "_miio._udp.local.", listener
        )

        time.sleep(timeout)
        browser.cancel()

        return listener.found_devices
