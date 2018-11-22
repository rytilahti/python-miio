import codecs
import inspect
import ipaddress
import logging
from functools import partial
from typing import Union, Callable, Dict, Optional  # noqa: F401

import zeroconf

from . import (Device, Vacuum, ChuangmiPlug, PowerStrip, AirPurifier, AirFresh, Ceil,
               PhilipsBulb, PhilipsEyecare, PhilipsMoonlight, ChuangmiIr,
               AirHumidifier, WaterPurifier, WifiSpeaker, WifiRepeater,
               Yeelight, Fan, Cooker, AirConditioningCompanion, AirQualityMonitor)

from .airconditioningcompanion import (MODEL_ACPARTNER_V1, MODEL_ACPARTNER_V2, MODEL_ACPARTNER_V3, )
from .airhumidifier import (MODEL_HUMIDIFIER_CA1, MODEL_HUMIDIFIER_V1, )
from .chuangmi_plug import (MODEL_CHUANGMI_PLUG_V1, MODEL_CHUANGMI_PLUG_V3,
                            MODEL_CHUANGMI_PLUG_M1, )
from .fan import (MODEL_FAN_V2, MODEL_FAN_V3, MODEL_FAN_SA1, MODEL_FAN_ZA1, )
from .powerstrip import (MODEL_POWER_STRIP_V1, MODEL_POWER_STRIP_V2, )

_LOGGER = logging.getLogger(__name__)


DEVICE_MAP = {
    "rockrobo-vacuum-v1": Vacuum,
    "roborock-vacuum-s5": Vacuum,
    "chuangmi-plug-m1": partial(ChuangmiPlug, model=MODEL_CHUANGMI_PLUG_M1),
    "chuangmi-plug-v2": partial(ChuangmiPlug, model=MODEL_CHUANGMI_PLUG_M1),
    "chuangmi-plug-v1": partial(ChuangmiPlug, model=MODEL_CHUANGMI_PLUG_V1),
    "chuangmi-plug_": partial(ChuangmiPlug, model=MODEL_CHUANGMI_PLUG_V1),
    "chuangmi-plug-v3": partial(ChuangmiPlug, model=MODEL_CHUANGMI_PLUG_V3),
    "qmi-powerstrip-v1": partial(PowerStrip, model=MODEL_POWER_STRIP_V1),
    "zimi-powerstrip-v2": partial(PowerStrip, model=MODEL_POWER_STRIP_V2),
    "zhimi-airpurifier-m1": AirPurifier,   # mini model
    "zhimi-airpurifier-m2": AirPurifier,   # mini model 2
    "zhimi-airpurifier-ma1": AirPurifier,  # ms model
    "zhimi-airpurifier-ma2": AirPurifier,  # ms model 2
    "zhimi-airpurifier-sa1": AirPurifier,  # super model
    "zhimi-airpurifier-sa2": AirPurifier,  # super model 2
    "zhimi-airpurifier-v1": AirPurifier,   # v1
    "zhimi-airpurifier-v2": AirPurifier,   # v2
    "zhimi-airpurifier-v3": AirPurifier,   # v3
    "zhimi-airpurifier-v5": AirPurifier,   # v5
    "zhimi-airpurifier-v6": AirPurifier,   # v6
    "zhimi-airpurifier-mc1": AirPurifier,  # mc1
    "chuangmi-ir-v2": ChuangmiIr,
    "zhimi-humidifier-v1": partial(AirHumidifier, model=MODEL_HUMIDIFIER_V1),
    "zhimi-humidifier-ca1": partial(AirHumidifier, model=MODEL_HUMIDIFIER_CA1),
    "yunmi-waterpuri-v2": WaterPurifier,
    "philips-light-bulb": PhilipsBulb,     # cannot be discovered via mdns
    "philips-light-candle": PhilipsBulb,   # cannot be discovered via mdns
    "philips-light-candle2": PhilipsBulb,  # cannot be discovered via mdns
    "philips-light-ceiling": Ceil,
    "philips-light-zyceiling": Ceil,
    "philips-light-sread1": PhilipsEyecare,  # name needs to be checked
    "philips-light-moonlight": PhilipsMoonlight,  # name needs to be checked
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
    "yeelink-light-": Yeelight,
    "zhimi-fan-v2": partial(Fan, model=MODEL_FAN_V2),
    "zhimi-fan-v3": partial(Fan, model=MODEL_FAN_V3),
    "zhimi-fan-sa1": partial(Fan, model=MODEL_FAN_SA1),
    "zhimi-fan-za1": partial(Fan, model=MODEL_FAN_ZA1),
    "zhimi-airfresh-va2": AirFresh,
    "zhimi-airmonitor-v1": AirQualityMonitor,
    "lumi-gateway-": lambda x: other_package_info(
        x, "https://github.com/Danielhiversen/PyXiaomiGateway")
}  # type: Dict[str, Union[Callable, Device]]


def pretty_token(token):
    """Return a pretty string presentation for a token."""
    return codecs.encode(token, 'hex').decode()


def other_package_info(info, desc):
    """Return information about another package supporting the device."""
    return "%s @ %s, check %s" % (
        info.name,
        ipaddress.ip_address(info.address),
        desc)


def create_device(name: str, addr: str, device_cls: partial) -> Device:
    """Return a device object for a zeroconf entry."""
    _LOGGER.debug("Found a supported '%s', using '%s' class",
                  name, device_cls.func.__name__)

    dev = device_cls(ip=addr)
    m = dev.do_discover()
    dev.token = m.checksum
    _LOGGER.info("Found a supported '%s' at %s - token: %s",
                 device_cls.func.__name__,
                 addr,
                 pretty_token(dev.token))
    return dev


class Listener:
    """mDNS listener creating Device objects based on detected devices."""
    def __init__(self):
        self.found_devices = {}  # type: Dict[str, Device]

    def check_and_create_device(self, info, addr) -> Optional[Device]:
        """Create a corresponding :class:`Device` implementation
         for a given info and address.."""
        name = info.name
        for identifier, v in DEVICE_MAP.items():
            if name.startswith(identifier):
                if inspect.isclass(v):
                    return create_device(name, addr, partial(v))
                elif type(v) is partial and inspect.isclass(v.func):
                    return create_device(name, addr, v)
                elif callable(v):
                    dev = Device(ip=addr)
                    _LOGGER.info("%s: token: %s",
                                 v(info),
                                 pretty_token(dev.do_discover().checksum))
                    return None
        _LOGGER.warning("Found unsupported device %s at %s, "
                        "please report to developers", name, addr)
        return None

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        addr = str(ipaddress.ip_address(info.address))
        if addr not in self.found_devices:
            dev = self.check_and_create_device(info, addr)
            self.found_devices[addr] = dev


class Discovery:
    """mDNS discoverer for miIO based devices (_miio._udp.local).
    Calling :func:`discover_mdns` will cause this to subscribe for updates
    on ``_miio._udp.local`` until any key is pressed, after which a dict
    of detected devices is returned."""
    @staticmethod
    def discover_mdns() -> Dict[str, Device]:
        """Discover devices with mdns until """
        _LOGGER.info("Discovering devices with mDNS, press any key to quit...")

        listener = Listener()
        browser = zeroconf.ServiceBrowser(
            zeroconf.Zeroconf(), "_miio._udp.local.", listener)

        input()  # to keep execution running until a key is pressed
        browser.cancel()

        return listener.found_devices
