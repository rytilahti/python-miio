"""Xiaomi Gateway device base class."""

import logging

from ..device import Device
from .gateway import Gateway

_LOGGER = logging.getLogger(__name__)


class GatewayDevice(Device):
    """GatewayDevice class Specifies the init method for all gateway device
    functionalities."""

    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
        parent: Gateway = None,
    ) -> None:
        if parent is not None:
            self._gateway = parent
        else:
            self._gateway = Device(ip, token, start_id, debug, lazy_discover)
            _LOGGER.debug(
                "Creating new device instance, only use this for cli interface"
            )
