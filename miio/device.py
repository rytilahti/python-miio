import logging
from enum import Enum
from inspect import getmembers
from typing import Any, Dict, List, Optional, Union  # noqa: F401

import click

from .click_common import DeviceGroupMeta, LiteralParamType, command, format_output
from .descriptors import (
    ActionDescriptor,
    EnumSettingDescriptor,
    SensorDescriptor,
    SettingDescriptor,
)
from .deviceinfo import DeviceInfo
from .devicestatus import DeviceStatus
from .exceptions import DeviceInfoUnavailableException, PayloadDecodeException
from .miioprotocol import MiIOProtocol

_LOGGER = logging.getLogger(__name__)


class UpdateState(Enum):
    Downloading = "downloading"
    Installing = "installing"
    Failed = "failed"
    Idle = "idle"


class Device(metaclass=DeviceGroupMeta):
    """Base class for all device implementations.

    This is the main class providing the basic protocol handling for devices using the
    ``miIO`` protocol. This class should not be initialized directly but a device-
    specific class inheriting it should be used instead of it.
    """

    retry_count = 3
    timeout = 5
    _mappings: Dict[str, Any] = {}
    _supported_models: List[str] = []

    def __init_subclass__(cls, **kwargs):
        """Overridden to register all integrations to the factory."""
        super().__init_subclass__(**kwargs)

        from .devicefactory import DeviceFactory

        DeviceFactory.register(cls)

    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
        timeout: int = None,
        *,
        model: str = None,
    ) -> None:
        self.ip = ip
        self.token: Optional[str] = token
        self._model: Optional[str] = model
        self._info: Optional[DeviceInfo] = None
        self._status: Optional[DeviceStatus] = None
        self._buttons: Optional[List[ButtonDescriptor]] = None
        self._actions: Optional[Dict[str, ActionDescriptor]] = None
        timeout = timeout if timeout is not None else self.timeout
        self._protocol = MiIOProtocol(
            ip, token, start_id, debug, lazy_discover, timeout
        )

    def send(
        self,
        command: str,
        parameters: Any = None,
        retry_count: int = None,
        *,
        extra_parameters=None,
    ) -> Any:
        """Send a command to the device.

        Basic format of the request:
        {"id": 1234, "method": command, "parameters": parameters}

        `extra_parameters` allows passing elements to the top-level of the request.
        This is necessary for some devices, such as gateway devices, which expect
        the sub-device identifier to be on the top-level.

        :param str command: Command to send
        :param dict parameters: Parameters to send
        :param int retry_count: How many times to retry on error
        :param dict extra_parameters: Extra top-level parameters
        :param str model: Force model to avoid autodetection
        """
        retry_count = retry_count if retry_count is not None else self.retry_count
        return self._protocol.send(
            command, parameters, retry_count, extra_parameters=extra_parameters
        )

    def send_handshake(self):
        """Send initial handshake to the device."""
        return self._protocol.send_handshake()

    @command(
        click.argument("command", type=str, required=True),
        click.argument("parameters", type=LiteralParamType(), required=False),
    )
    def raw_command(self, command, parameters):
        """Send a raw command to the device. This is mostly useful when trying out
        commands which are not implemented by a given device instance.

        :param str command: Command to send
        :param dict parameters: Parameters to send
        """
        return self.send(command, parameters)

    @command(
        default_output=format_output(
            "",
            "Model: {result.model}\n"
            "Hardware version: {result.hardware_version}\n"
            "Firmware version: {result.firmware_version}\n",
        ),
        skip_autodetect=True,
    )
    def info(self, *, skip_cache=False) -> DeviceInfo:
        """Get (and cache) miIO protocol information from the device.

        This includes information about connected wlan network, and hardware and
        software versions.

        :param skip_cache bool: Skip the cache
        """
        if self._info is not None and not skip_cache:
            return self._info

        return self._fetch_info()

    def _fetch_info(self) -> DeviceInfo:
        """Perform miIO.info query on the device and cache the result."""
        try:
            devinfo = DeviceInfo(self.send("miIO.info"))
            self._info = devinfo
            _LOGGER.debug("Detected model %s", devinfo.model)
            cls = self.__class__.__name__
            bases = ["Device", "MiotDevice"]
            if devinfo.model not in self.supported_models and cls not in bases:
                _LOGGER.warning(
                    "Found an unsupported model '%s' for class '%s'. If this is working for you, please open an issue at https://github.com/rytilahti/python-miio/",
                    devinfo.model,
                    cls,
                )

            return devinfo
        except PayloadDecodeException as ex:
            raise DeviceInfoUnavailableException(
                "Unable to request miIO.info from the device"
            ) from ex

    @property
    def device_id(self) -> int:
        """Return device id (did), if available."""
        if not self._protocol._device_id:
            self.send_handshake()
        return int.from_bytes(self._protocol._device_id, byteorder="big")

    @property
    def raw_id(self) -> int:
        """Return the last used protocol sequence id."""
        return self._protocol.raw_id

    @property
    def supported_models(self) -> List[str]:
        """Return a list of supported models."""
        return list(self._mappings.keys()) or self._supported_models

    @property
    def model(self) -> str:
        """Return device model."""
        if self._model is not None:
            return self._model

        return self.info().model

    def update(self, url: str, md5: str):
        """Start an OTA update."""
        payload = {
            "mode": "normal",
            "install": "1",
            "app_url": url,
            "file_md5": md5,
            "proc": "dnld install",
        }
        return self.send("miIO.ota", payload)[0] == "ok"

    def update_progress(self) -> int:
        """Return current update progress [0-100]."""
        return self.send("miIO.get_ota_progress")[0]

    def update_state(self):
        """Return current update state."""
        return UpdateState(self.send("miIO.get_ota_state")[0])

    def configure_wifi(self, ssid, password, uid=0, extra_params=None):
        """Configure the wifi settings."""
        if extra_params is None:
            extra_params = {}
        params = {"ssid": ssid, "passwd": password, "uid": uid, **extra_params}

        return self.send("miIO.config_router", params)[0]

    def get_properties(
        self, properties, *, property_getter="get_prop", max_properties=None
    ):
        """Request properties in slices based on given max_properties.

        This is necessary as some devices have limitation on how many
        properties can be queried at once.

        If `max_properties` is None, all properties are requested at once.

        :param list properties: List of properties to query from the device.
        :param int max_properties: Number of properties that can be requested at once.
        :return: List of property values.
        """
        _props = properties.copy()
        values = []
        while _props:
            values.extend(self.send(property_getter, _props[:max_properties]))
            if max_properties is None:
                break

            _props[:] = _props[max_properties:]

        properties_count = len(properties)
        values_count = len(values)
        if properties_count != values_count:
            _LOGGER.debug(
                "Count (%s) of requested properties does not match the "
                "count (%s) of received values.",
                properties_count,
                values_count,
            )

        return values

    def status(self) -> DeviceStatus:
        """Return device status."""
        raise NotImplementedError()


    def cached_status(self) -> DeviceStatus:
        """Return device status from cache."""
        if self._status is None:
            self._status = self.status()

        return self._status

    def actions(self) -> Dict[str, ActionDescriptor]:
        """Return device actions."""
        if self._actions is None:
            self._actions = {}
            for action_tuple in getmembers(self, lambda o: hasattr(o, "_action")):
                method_name, method = action_tuple
                action = method._action
                action.method = method  # bind the method
                self._actions[method_name] = action

        return self._actions

    def settings(self) -> Dict[str, SettingDescriptor]:
        """Return list of settings."""
        settings = (
            self.cached_status().settings()
        )  # NOTE that this already does IO so schould be run in executer job in HA
        for setting in settings.values():
            # TODO: Bind setter methods, this should probably done only once during init.
            if setting.setter is None:
                # TODO: this is ugly, how to fix the issue where setter_name is optional and thus not acceptable for getattr?
                if setting.setter_name is None:
                    raise Exception(
                        f"Neither setter or setter_name was defined for {setting}"
                    )

                setting.setter = getattr(self, setting.setter_name)
            if (
                isinstance(setting, EnumSettingDescriptor)
                and setting.choices_attribute is not None
            ):
                retrieve_choices_function = getattr(self, setting.choices_attribute)
                setting.choices = retrieve_choices_function()  # This can do IO

        return settings

    def sensors(self) -> Dict[str, SensorDescriptor]:
        """Return sensors."""
        sensors = self.cached_status().sensors()
        return sensors

    def __repr__(self):
        return f"<{self.__class__.__name__ }: {self.ip} (token: {self.token})>"
