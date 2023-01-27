import logging
import time
from ipaddress import ip_address
from typing import Dict, Optional

import zeroconf

from miio import Device, DeviceFactory

_LOGGER = logging.getLogger(__name__)


class Listener(zeroconf.ServiceListener):
    """mDNS listener creating Device objects based on detected devices."""

    def __init__(self):
        self.found_devices: Dict[str, Device] = {}

    def create_device(self, info, addr) -> Optional[Device]:
        """Get a device instance for a mdns response."""
        name = info.name
        # e.g. XXXX in the name could be a
        # yeelink-light-color1_miioXXXX._miio._udp.local.
        _LOGGER.debug("Got mdns name: %s", name)

        model, _ = name.split("_", maxsplit=1)
        model = model.replace("-", ".")

        _LOGGER.info("Found '%s' at %s, performing handshake", model, addr)
        try:
            dev = DeviceFactory.class_for_model(model)(str(addr))
            res = dev.send_handshake()

            devid = int.from_bytes(res.header.value.device_id, byteorder="big")
            ts = res.header.value.ts

            _LOGGER.info("Handshake successful! devid: %s, ts: %s", devid, ts)
        except Exception as ex:
            _LOGGER.warning("Handshake failed: %s", ex)
            return None

        return dev

    def add_service(self, zeroconf: "zeroconf.Zeroconf", type_: str, name: str) -> None:
        """Callback for discovery responses."""
        info = zeroconf.get_service_info(type_, name)
        addr = ip_address(info.addresses[0])

        if addr not in self.found_devices:
            dev = self.create_device(info, addr)
            if dev is not None:
                self.found_devices[str(addr)] = dev

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
