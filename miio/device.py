import binascii
import codecs
import datetime
import logging
import socket
from enum import Enum
from typing import Any, List, Optional  # noqa: F401

import click
import construct

from .click_common import (
    DeviceGroupMeta, command, format_output, LiteralParamType
)
from .exceptions import DeviceException, DeviceError
from .protocol import Message

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
            self.data["token"])

    def __json__(self):
        return self.data

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
    def __init__(self, ip: str = None, token: str = None,
                 start_id: int=0, debug: int=0, lazy_discover: bool=True) -> None:
        """
        Create a :class:`Device` instance.
        :param ip: IP address or a hostname for the device
        :param token: Token used for encryption
        :param start_id: Running message id sent to the device
        :param debug: Wanted debug level
        """
        self.ip = ip
        self.port = 54321
        if token is None:
            token = 32 * '0'
        if token is not None:
            self.token = bytes.fromhex(token)
        self.debug = debug
        self.lazy_discover = lazy_discover

        self._timeout = 5
        self._discovered = False
        self._device_ts = None  # type: datetime.datetime
        self.__id = start_id
        self._device_id = None

    def do_discover(self) -> Message:
        """Send a handshake to the device,
        which can be used to the device type and serial.
        The handshake must also be done regularly to enable communication
        with the device.

        :rtype: Message

        :raises DeviceException: if the device could not be discovered."""
        m = Device.discover(self.ip)
        if m is not None:
            self._device_id = m.header.value.device_id
            self._device_ts = m.header.value.ts
            self._discovered = True
            if self.debug > 1:
                _LOGGER.debug(m)
            _LOGGER.debug("Discovered %s with ts: %s, token: %s",
                          binascii.hexlify(self._device_id).decode(),
                          self._device_ts,
                          codecs.encode(m.checksum, 'hex'))
        else:
            _LOGGER.error("Unable to discover a device at address %s", self.ip)
            raise DeviceException("Unable to discover the device %s" % self.ip)

        return m

    @staticmethod
    def discover(addr: str=None) -> Any:
        """Scan for devices in the network.
        This method is used to discover supported devices by sending a
        handshake message to the broadcast address on port 54321.
        If the target IP address is given, the handshake will be send as
        an unicast packet.

        :param str addr: Target IP address"""
        timeout = 5
        is_broadcast = addr is None
        seen_addrs = []  # type: List[str]
        if is_broadcast:
            addr = '<broadcast>'
            is_broadcast = True
            _LOGGER.info("Sending discovery to %s with timeout of %ss..",
                         addr, timeout)
        # magic, length 32
        helobytes = bytes.fromhex(
            '21310020ffffffffffffffffffffffffffffffffffffffffffffffffffffffff')

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.settimeout(timeout)
        s.sendto(helobytes, (addr, 54321))
        while True:
            try:
                data, addr = s.recvfrom(1024)
                m = Message.parse(data)  # type: Message
                _LOGGER.debug("Got a response: %s", m)
                if not is_broadcast:
                    return m

                if addr[0] not in seen_addrs:
                    _LOGGER.info("  IP %s (ID: %s) - token: %s",
                                 addr[0],
                                 binascii.hexlify(m.header.value.device_id).decode(),
                                 codecs.encode(m.checksum, 'hex'))
                    seen_addrs.append(addr[0])
            except socket.timeout:
                if is_broadcast:
                    _LOGGER.info("Discovery done")
                return  # ignore timeouts on discover
            except Exception as ex:
                _LOGGER.warning("error while reading discover results: %s", ex)
                break

    def send(self, command: str, parameters: Any=None, retry_count=3) -> Any:
        """Build and send the given command.
        Note that this will implicitly call :func:`do_discover` to do a handshake,
        and will re-try in case of errors while incrementing the `_id` by 100.

        :param str command: Command to send
        :param dict parameters: Parameters to send, or an empty list FIXME
        :param retry_count: How many times to retry in case of failure
        :raises DeviceException: if an error has occured during communication."""

        if not self.lazy_discover or not self._discovered:
            self.do_discover()

        cmd = {
            "id": self._id,
            "method": command,
        }

        if parameters is not None:
            cmd["params"] = parameters
        else:
            cmd["params"] = []

        send_ts = self._device_ts + datetime.timedelta(seconds=1)
        header = {'length': 0, 'unknown': 0x00000000,
                  'device_id': self._device_id, 'ts': send_ts}

        msg = {'data': {'value': cmd},
               'header': {'value': header},
               'checksum': 0}
        m = Message.build(msg, token=self.token)
        _LOGGER.debug("%s:%s >>: %s", self.ip, self.port, cmd)
        if self.debug > 1:
            _LOGGER.debug("send (timeout %s): %s",
                          self._timeout, Message.parse(m, token=self.token))

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(self._timeout)

        try:
            s.sendto(m, (self.ip, self.port))
        except OSError as ex:
            _LOGGER.error("failed to send msg: %s", ex)
            raise DeviceException from ex

        try:
            data, addr = s.recvfrom(1024)
            m = Message.parse(data, token=self.token)
            self._device_ts = m.header.value.ts
            if self.debug > 1:
                _LOGGER.debug("recv from %s: %s", addr[0], m)

            self.__id = m.data.value["id"]
            _LOGGER.debug("%s:%s (ts: %s, id: %s) << %s",
                          self.ip, self.port,
                          m.header.value.ts,
                          m.data.value["id"],
                          m.data.value)
            if "error" in m.data.value:
                raise DeviceError(m.data.value["error"])

            try:
                return m.data.value["result"]
            except KeyError:
                return m.data.value
        except construct.core.ChecksumError as ex:
            raise DeviceException("Got checksum error which indicates use "
                                  "of an invalid token. "
                                  "Please check your token!") from ex
        except OSError as ex:
            if retry_count > 0:
                _LOGGER.debug("Retrying with incremented id, "
                              "retries left: %s", retry_count)
                self.__id += 100
                self._discovered = False
                return self.send(command, parameters, retry_count - 1)

            _LOGGER.error("Got error when receiving: %s", ex)
            raise DeviceException("No response from the device") from ex

    @command(
        click.argument('command', type=str, required=True),
        click.argument('parameters', type=LiteralParamType(), required=False),
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
            "Firmware version: {result.firmware_version}\n"
            "Network: {result.network_interface}\n"
            "AP: {result.accesspoint}\n")
    )
    def info(self) -> DeviceInfo:
        """Get miIO protocol information from the device.
        This includes information about connected wlan network,
        and harware and software versions."""
        return DeviceInfo(self.send("miIO.info"))

    def update(self, url: str, md5: str):
        """Start an OTA update."""
        payload = {
            "mode": "normal",
            "install": "1",
            "app_url": url,
            "file_md5": md5,
            "proc": "dnld install"
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
        params = {"ssid": ssid, "passwd": password, "uid": uid,
                  **extra_params}

        return self.send("miIO.config_router", params)[0]

    @property
    def _id(self) -> int:
        """Increment and return the sequence id."""
        self.__id += 1
        if self.__id >= 9999:
            self.__id = 1
        return self.__id

    @property
    def raw_id(self) -> int:
        """Return the sequence id."""
        return self.__id
