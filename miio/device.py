import logging
from enum import Enum
from typing import Any, Optional  # noqa: F401

import click

from .click_common import DeviceGroupMeta, LiteralParamType, command, format_output
from .exceptions import DeviceInfoUnavailableException, PayloadDecodeException
from .miioprotocol import MiIOProtocol

_LOGGER = logging.getLogger(__name__)


class UpdateState(Enum):
    Downloading = "downloading"
    Installing = "installing"
    Failed = "failed"
    Idle = "idle"


class DeviceInfo:
    """Container of miIO device information.
    Hardware properties such as device model, MAC address, memory information,
    and hardware and software information is contained here."""

    def __init__(self, data):
        """
        Response of a Xiaomi Smart WiFi Plug

        {'ap': {'bssid': 'FF:FF:FF:FF:FF:FF', 'rssi': -68, 'ssid': 'network'},
         'cfg_time': 0,
         'fw_ver': '1.2.4_16',
         'hw_ver': 'MW300',
         'life': 24,
         'mac': '28:FF:FF:FF:FF:FF',
         'mmfree': 30312,
         'model': 'chuangmi.plug.m1',
         'netif': {'gw': '192.168.xxx.x',
                   'localIp': '192.168.xxx.x',
                   'mask': '255.255.255.0'},
         'ot': 'otu',
         'ott_stat': [0, 0, 0, 0],
         'otu_stat': [320, 267, 3, 0, 3, 742],
         'token': '2b00042f7481c7b056c4b410d28f33cf',
         'wifi_fw_ver': 'SD878x-14.76.36.p84-702.1.0-WM'}
        """
        self.data = data

    def __repr__(self):
        return "%s v%s (%s) @ %s - token: %s" % (
            self.data["model"],
            self.data["fw_ver"],
            self.data["mac"],
            self.network_interface["localIp"],
            self.data["token"],
        )

    @property
    def network_interface(self):
        """Information about network configuration."""
        return self.data["netif"]

    @property
    def accesspoint(self):
        """Information about connected wlan accesspoint."""
        return self.data["ap"]

    @property
    def model(self) -> Optional[str]:
        """Model string if available."""
        if self.data["model"] is not None:
            return self.data["model"]
        return None

    @property
    def firmware_version(self) -> Optional[str]:
        """Firmware version if available."""
        if self.data["fw_ver"] is not None:
            return self.data["fw_ver"]
        return None

    @property
    def hardware_version(self) -> Optional[str]:
        """Hardware version if available."""
        if self.data["hw_ver"] is not None:
            return self.data["hw_ver"]
        return None

    @property
    def mac_address(self) -> Optional[str]:
        """MAC address if available."""
        if self.data["mac"] is not None:
            return self.data["mac"]
        return None

    @property
    def raw(self):
        """Raw data as returned by the device."""
        return self.data


class Device(metaclass=DeviceGroupMeta):
    """Base class for all device implementations.
    This is the main class providing the basic protocol handling for devices using
    the ``miIO`` protocol.
    This class should not be initialized directly but a device-specific class inheriting
    it should be used instead of it."""

    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
    ) -> None:
        self.ip = ip
        self.token = token
        self._protocol = MiIOProtocol(ip, token, start_id, debug, lazy_discover)

    def send(
        self,
        command: str,
        parameters: Any = None,
        retry_count=3,
        *,
        extra_parameters=None
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
        """
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
        """Send a raw command to the device.
        This is mostly useful when trying out commands which are not
        implemented by a given device instance.

        :param str command: Command to send
        :param dict parameters: Parameters to send"""
        return self.send(command, parameters)

    @command(
        default_output=format_output(
            "",
            "Model: {result.model}\n"
            "Hardware version: {result.hardware_version}\n"
            "Firmware version: {result.firmware_version}\n",
        )
    )
    def info(self) -> DeviceInfo:
        """Get miIO protocol information from the device.
        This includes information about connected wlan network,
        and hardware and software versions."""
        try:
            return DeviceInfo(self.send("miIO.info"))
        except PayloadDecodeException as ex:
            raise DeviceInfoUnavailableException(
                "Unable to request miIO.info from the device"
            ) from ex

    @property
    def raw_id(self):
        """Return the last used protocol sequence id."""
        return self._protocol.raw_id

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
        :return List of property values.
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
