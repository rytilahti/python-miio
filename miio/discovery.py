import logging
import zeroconf
import ipaddress
import inspect
import codecs
from . import (Device, Vacuum, Plug, PlugV1, PowerStrip, AirPurifier, Ceil,
               PhilipsBulb, PhilipsEyecare, ChuangmiIr, AirHumidifier,
               WaterPurifier, WifiSpeaker, Yeelight)
from typing import Union, Callable, Dict, Optional  # noqa: F401


_LOGGER = logging.getLogger(__name__)


DEVICE_MAP = {
    "rockrobo-vacuum-v1": Vacuum,
    "roborock-vacuum-s5": Vacuum,
    "chuangmi-plug-m1": Plug,
    "chuangmi-plug-v2": Plug,
    "chuangmi-plug-v1": PlugV1,
    "chuangmi-plug_": PlugV1,
    "qmi-powerstrip-v1": PowerStrip,
    "zimi-powerstrip-v2": PowerStrip,
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
    "chuangmi-ir-v2": ChuangmiIr,
    "zhimi-humidifier-v1": AirHumidifier,
    "zhimi-humidifier-ca1": AirHumidifier,
    "yunmi-waterpuri-v2": WaterPurifier,
    # It looks like philips devices cannot be discovered via mdns
    "philips-light-bulb": PhilipsBulb,
    "philips-light-ceiling": Ceil,
    "philips-light-sread1": PhilipsEyecare,
    "xiaomi-wifispeaker-v1": WifiSpeaker,  # name needs to be checked
    "yeelink-light-": Yeelight,
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


def create_device(addr, device_cls) -> Device:
    """Return a device object for a zeroconf entry."""
    dev = device_cls(ip=addr)
    m = dev.do_discover()
    dev.token = m.checksum
    _LOGGER.info("Found a supported '%s' at %s - token: %s",
                 device_cls.__name__,
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
                    _LOGGER.debug("Found a supported '%s', using '%s' class",
                                  name, v.__name__)
                    return create_device(addr, v)
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
