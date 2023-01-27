"""Xiaomi Gateway device base class."""

import logging
from typing import TYPE_CHECKING, List, Optional

from miio import DeviceException

_LOGGER = logging.getLogger(__name__)

# Necessary due to circular deps
if TYPE_CHECKING:
    from .gateway import Gateway


class GatewayDevice:
    """GatewayDevice class Specifies the init method for all gateway device
    functionalities."""

    _supported_models = ["dummy.device"]

    def __init__(
        self,
        parent: Optional["Gateway"] = None,
    ) -> None:
        if parent is None:
            raise DeviceException(
                "This should never be initialized without gateway object."
            )

        self._gateway = parent
        self._event_ids: List[str] = []
