import logging
import zeroconf
import ipaddress
import inspect
import codecs
from typing import Any, List, Union, Callable
from mirobo import Message, Device, Vacuum

_LOGGER = logging.getLogger(__name__)


def other_package_info(info, desc):
    return "%s @ %s, check %s" % (info.name, ipaddress.ip_address(info.address), desc)


class Listener:
    def __init__(self):
        self.found_devices = {}
    def _check_if_supported(self, info, addr):
        name = info.name
        for k, v in Discovery._mdns_device_map.items():
            if name.startswith(k):
                if inspect.isclass(v):
                    dev = v(ip=addr)
                    m = dev.do_discover()
                    dev.token = m.checksum
                    _LOGGER.info("Found supported '%s' at %s:%s (%s) token: %s" % (
                        v.__name__, addr, info.port, name, dev.token))
                    return dev
                elif callable(v):
                    _LOGGER.info(v(info))
                    dev = Device(ip=addr)
                    _LOGGER.info("token: %s" % codecs.encode(dev.do_discover().checksum, 'hex'))
                    return None
        _LOGGER.warning("Found unsupported device %s at %s, please report to developers" % (name, addr))
        return None

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        addr = str(ipaddress.ip_address(info.address))
        if addr not in self.found_devices:
            dev = self._check_if_supported(info, addr)
            self.found_devices[addr] = dev


class Discovery:
    _mdns_device_map = {
        "rockrobo-vacuum-v1": Vacuum,
        "yeelink-light-": lambda x: other_package_info(x, "python-yeelight package"),
        "lumi-gateway-": lambda x: other_package_info(x, "https://github.com/Danielhiversen/PyXiaomiGateway")
    } # type: Dict[str, Union[Callable, Device]]

    @staticmethod
    def discover_mdns():
        _LOGGER.info("Discovering devices with mDNS, press any key to quit...")

        listener = Listener()
        browser = zeroconf.ServiceBrowser(zeroconf.Zeroconf(), "_miio._udp.local.", listener)

        input()  # to keep execution running until a key is pressed
        browser.cancel()

        return listener.found_devices