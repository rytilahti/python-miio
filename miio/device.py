import logging
from enum import Enum
from inspect import getmembers
from typing import Any, Dict, List, Optional, Union, cast, final  # noqa: F401

import click

from .click_common import DeviceGroupMeta, LiteralParamType, command, format_output
from .descriptors import (
    AccessFlags,
    ActionDescriptor,
    EnumDescriptor,
    PropertyConstraint,
    PropertyDescriptor,
    RangeDescriptor,
)
from .deviceinfo import DeviceInfo
from .devicestatus import DeviceStatus
from .exceptions import (
    DeviceError,
    DeviceInfoUnavailableException,
    PayloadDecodeException,
    UnsupportedFeatureException,
)
from .miioprotocol import MiIOProtocol

_LOGGER = logging.getLogger(__name__)


class UpdateState(Enum):
    Downloading = "downloading"
    Installing = "installing"
    Failed = "failed"
    Idle = "idle"


def _info_output(result):
    """Format the output for info command."""
    s = f"Model: {result.model}\n"
    s += f"Hardware version: {result.hardware_version}\n"
    s += f"Firmware version: {result.firmware_version}\n"

    from .devicefactory import DeviceFactory

    cls = DeviceFactory.class_for_model(result.model)
    dev = DeviceFactory.create(result.ip_address, result.token, force_generic_miot=True)
    s += f"Supported using: {cls.__name__}\n"
    s += f"Command: miiocli {cls.__name__.lower()} --ip {result.ip_address} --token {result.token}\n"
    s += f"Supported by genericmiot: {dev.supports_miot()}"

    return s


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
        ip: Optional[str] = None,
        token: Optional[str] = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
        timeout: Optional[int] = None,
        *,
        model: Optional[str] = None,
    ) -> None:
        self.ip = ip
        self.token: Optional[str] = token
        self._model: Optional[str] = model
        self._info: Optional[DeviceInfo] = None
        self._actions: Optional[Dict[str, ActionDescriptor]] = None
        self._properties: Optional[Dict[str, PropertyDescriptor]] = None
        timeout = timeout if timeout is not None else self.timeout
        self._debug = debug
        self._protocol = MiIOProtocol(
            ip, token, start_id, debug, lazy_discover, timeout
        )

    def send(
        self,
        command: str,
        parameters: Optional[Any] = None,
        retry_count: Optional[int] = None,
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
        default_output=format_output(result_msg_fmt=_info_output),
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
            # Ignore bases and generic classes
            bases = ["Device", "MiotDevice", "GenericMiot"]
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

    def _set_constraints_from_attributes(
        self, status: DeviceStatus
    ) -> Dict[str, PropertyDescriptor]:
        """Get the setting descriptors from a DeviceStatus."""
        properties = status.properties()
        unsupported_settings = []
        for key, prop in properties.items():
            if prop.setter_name is not None:
                prop.setter = getattr(self, prop.setter_name)
            if prop.setter is None:
                raise Exception(f"Neither setter or setter_name was defined for {prop}")

            if prop.constraint == PropertyConstraint.Choice:
                prop = cast(EnumDescriptor, prop)
                if prop.choices_attribute is not None:
                    retrieve_choices_function = getattr(self, prop.choices_attribute)
                    try:
                        prop.choices = retrieve_choices_function()
                    except UnsupportedFeatureException:
                        # TODO: this should not be done here
                        unsupported_settings.append(key)
                        continue

            elif prop.constraint == PropertyConstraint.Range:
                prop = cast(RangeDescriptor, prop)
                if prop.range_attribute is not None:
                    range_def = getattr(self, prop.range_attribute)
                    prop.min_value = range_def.min_value
                    prop.max_value = range_def.max_value
                    prop.step = range_def.step

            else:
                _LOGGER.debug("Got a regular setting without constraints: %s", prop)

        for unsupp_key in unsupported_settings:
            properties.pop(unsupp_key)

        return properties

    def _action_descriptors(self) -> Dict[str, ActionDescriptor]:
        """Get the action descriptors from a DeviceStatus."""
        actions = {}
        for action_tuple in getmembers(self, lambda o: hasattr(o, "_action")):
            method_name, method = action_tuple
            action = method._action
            action.method = method  # bind the method
            actions[action.id] = action

        return actions

    def _initialize_descriptors(self) -> None:
        """Cache all the descriptors once on the first call."""
        status = self.status()

        self._properties = self._set_constraints_from_attributes(status)
        self._actions = self._action_descriptors()

    @property
    def device_id(self) -> int:
        """Return the device id (did)."""
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

    def actions(self) -> Dict[str, ActionDescriptor]:
        """Return device actions."""
        if self._actions is None:
            self._initialize_descriptors()

        # TODO: we ignore the return value for now as these should always be initialized
        return self._actions  # type: ignore[return-value]

    def properties(self) -> Dict[str, PropertyDescriptor]:
        """Return all device properties."""
        if self._properties is None:
            self._initialize_descriptors()

        # TODO: we ignore the return value for now as these should always be initialized
        return self._properties  # type: ignore[return-value]

    @final
    def settings(self) -> Dict[str, PropertyDescriptor]:
        """Return settable properties."""
        if self._properties is None:
            self._initialize_descriptors()

        return {
            prop.id: prop
            for prop in self.properties().values()
            if prop.access & AccessFlags.Write
        }

    @final
    def sensors(self) -> Dict[str, PropertyDescriptor]:
        """Return read-only properties."""
        if self._properties is None:
            self._initialize_descriptors()

        return {
            prop.id: prop
            for prop in self.properties().values()
            if prop.access ^ AccessFlags.Write
        }

    def supports_miot(self) -> bool:
        """Return True if the device supports miot commands.

        This requests a single property (siid=1, piid=1) and returns True on success.
        """
        try:
            self.send("get_properties", [{"did": "dummy", "siid": 1, "piid": 1}])
        except DeviceError as ex:
            _LOGGER.debug("miot query failed, likely non-miot device: %s", repr(ex))
            return False
        return True

    def __repr__(self):
        return f"<{self.__class__.__name__ }: {self.ip} (token: {self.token})>"
