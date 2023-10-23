import logging
from enum import Enum
from typing import Any, Dict, List, Optional, Union, cast, final  # noqa: F401

import click

from .click_common import DeviceGroupMeta, LiteralParamType, command
from .descriptorcollection import DescriptorCollection
from .descriptors import AccessFlags, ActionDescriptor, Descriptor, PropertyDescriptor
from .deviceinfo import DeviceInfo
from .devicestatus import DeviceStatus
from .exceptions import (
    DeviceError,
    DeviceInfoUnavailableException,
    PayloadDecodeException,
)
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
        # TODO: use _info's noneness instead?
        self._initialized: bool = False
        self._descriptors: DescriptorCollection = DescriptorCollection(device=self)
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

            return devinfo
        except PayloadDecodeException as ex:
            raise DeviceInfoUnavailableException(
                "Unable to request miIO.info from the device"
            ) from ex

    def _initialize_descriptors(self) -> None:
        """Initialize the device descriptors.

        This will add descriptors defined in the implementation class and the status class.

        This can be overridden to add additional descriptors to the device.
        If you do so, do not forget to call this method.
        """
        self._descriptors.descriptors_from_object(self)

        # Read descriptors from the status class
        self._descriptors.descriptors_from_object(self.status.__annotations__["return"])

        if not self._descriptors:
            _LOGGER.warning(
                "'%s' does not specify any descriptors, please considering creating a PR.",
                self.__class__.__name__,
            )

        self._initialized = True

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

    @command()
    def status(self) -> DeviceStatus:
        """Return device status."""
        raise NotImplementedError()

    @command()
    def descriptors(self) -> DescriptorCollection[Descriptor]:
        """Return a collection containing all descriptors for the device."""
        if not self._initialized:
            self._initialize_descriptors()

        return self._descriptors

    @command()
    def actions(self) -> DescriptorCollection[ActionDescriptor]:
        """Return device actions."""
        return DescriptorCollection(
            {
                k: v
                for k, v in self.descriptors().items()
                if isinstance(v, ActionDescriptor)
            },
            device=self,
        )

    @final
    @command()
    def settings(self) -> DescriptorCollection[PropertyDescriptor]:
        """Return settable properties."""
        return DescriptorCollection(
            {
                k: v
                for k, v in self.descriptors().items()
                if isinstance(v, PropertyDescriptor) and v.access & AccessFlags.Write
            },
            device=self,
        )

    @final
    @command()
    def sensors(self) -> DescriptorCollection[PropertyDescriptor]:
        """Return read-only properties."""
        return DescriptorCollection(
            {
                k: v
                for k, v in self.descriptors().items()
                if isinstance(v, PropertyDescriptor) and v.access & AccessFlags.Read
            },
            device=self,
        )

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

    @command(
        click.argument("name"),
        click.argument("params", type=LiteralParamType(), required=False),
        name="call",
    )
    def call_action(self, name: str, params=None):
        """Call action by name."""
        try:
            act = self.actions()[name]
        except KeyError:
            raise ValueError("Unable to find action '%s'" % name)

        if params is None:
            return act.method()

        return act.method(params)

    @command(
        click.argument("name"),
        click.argument("params", type=LiteralParamType(), required=True),
        name="set",
    )
    def change_setting(self, name: str, params=None):
        """Change setting value."""
        try:
            setting = self.settings()[name]
        except KeyError:
            raise ValueError("Unable to find setting '%s'" % name)

        params = params if params is not None else []

        return setting.setter(params)

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.ip} (token: {self.token})>"
