"""Xiaomi Gateway device base class."""

import logging
from typing import TYPE_CHECKING

from ..device import Device
from ..exceptions import DeviceException

_LOGGER = logging.getLogger(__name__)

# Necessary due to circular deps
if TYPE_CHECKING:
    from .gateway import Gateway


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
        parent: "Gateway" = None,
    ) -> None:
        if parent is None:
            raise DeviceException(
                "This should never be initialized without gateway object."
            )

        self._gateway = parent
        super().__init__(ip, token, start_id, debug, lazy_discover)
