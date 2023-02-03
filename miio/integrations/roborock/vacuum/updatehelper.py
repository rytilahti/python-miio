import logging
from typing import Callable, Dict

from miio import DeviceException, DeviceStatus

_LOGGER = logging.getLogger(__name__)


class UpdateHelper:
    """Helper class to construct status containers using multiple status methods.

    This is used to perform status fetching on integrations that require calling
     multiple methods, some of which may not be supported by the target device.

    This class automatically removes the methods that failed from future updates,
    to avoid unnecessary device I/O.
    """

    def __init__(self, main_update_method: Callable):
        self._update_methods: Dict[str, Callable] = {}
        self._main_update_method = main_update_method

    def add_update_method(self, name: str, update_method: Callable):
        """Add status method to be called."""
        _LOGGER.debug(f"Adding {name} to update cycle: {update_method}")
        self._update_methods[name] = update_method

    def status(self) -> DeviceStatus:
        statuses = self._update_methods.copy()
        main_status = self._main_update_method()
        for name, method in statuses.items():
            try:
                main_status.embed(name, method())
                _LOGGER.debug(f"Success for {name}")
            except DeviceException as ex:
                _LOGGER.debug(
                    "Unable to query %s, removing from next query: %s", name, ex
                )
                self._update_methods.pop(name)

        return main_status
