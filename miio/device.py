import codecs
import datetime
import socket
import logging
from typing import Any, List, Optional  # noqa: F401

from .protocol import Message

_LOGGER = logging.getLogger(__name__)


class DeviceException(Exception):
    pass


class DeviceInfo:
    """Presentation of miIO device information."""
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

    @property
    def network_interface(self):
        """Return information about network configuration."""
        return self.data["netif"]

    @property
    def accesspoint(self):
        """Return information about connected wlan accesspoint."""
        return self.data["ap"]

    @property
    def model(self) -> Optional[str]:
        if self.data["model"] is not None:
            return self.data["model"]
        return None

    @property
    def firmware_version(self) -> Optional[str]:
        if self.data["fw_ver"] is not None:
            return self.data["fw_ver"]
        return None

    @property
    def hardware_version(self) -> Optional[str]:
        if self.data["hw_ver"] is not None:
            return self.data["hw_ver"]
        return None

    @property
    def raw(self):
        """Return raw data returned by the device."""
        return self.data


class Device:
    """Base class for all device implementations."""
    def __init__(self, ip: str = None, token: str = None,
                 start_id: int=0, debug: int=0) -> None:
        self.ip = ip
        self.port = 54321
        if token is None:
            token = 32 * '0'
        if token is not None:
            self.token = bytes.fromhex(token)
        self.debug = debug

        self._timeout = 5
        self._device_ts = None  # type: datetime.datetime
        self.__id = start_id
        self._devtype = None
        self._serial = None

    def do_discover(self) -> Message:
        """Does a discover to fetch the device type and serial.
        Raises a DeviceException if the device could not be discovered."""
        m = Device.discover(self.ip)
        if m is not None:
            self._devtype = m.header.value.devtype
            self._serial = m.header.value.serial
            self._device_ts = m.header.value.ts
            if self.debug > 1:
                _LOGGER.debug(m)
            _LOGGER.debug("Discovered %s %s with ts: %s, token: %s",
                          self._devtype,
                          self._serial,
                          self._device_ts,
                          codecs.encode(m.checksum, 'hex'))
        else:
            _LOGGER.error("Unable to discover a device at address %s", self.ip)
            raise DeviceException("Unable to discover the device %s" % self.ip)

        return m

    @staticmethod
    def discover(addr: str=None) -> Any:
        """Scan for devices in the network."""
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
                    _LOGGER.info("  IP %s: %s - token: %s",
                                 addr[0],
                                 m.header.value.devtype,
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
        """Build and send the given command."""
        self.do_discover()

        cmd = {
            "id": self._id,
            "method": command,
        }

        if parameters is not None:
            cmd["params"] = parameters

        send_ts = self._device_ts + datetime.timedelta(seconds=1)
        header = {'length': 0, 'unknown': 0x00000000,
                  'devtype': self._devtype, 'serial': self._serial,
                  'ts': send_ts}

        msg = {'data': {'value': cmd},
               'header': {'value': header},
               'checksum': 0}
        ctx = {'token': self.token}
        m = Message.build(msg, ctx)
        _LOGGER.debug("%s:%s >>: %s", self.ip, self.port, cmd)
        if self.debug > 1:
            _LOGGER.debug("send (timeout %s): %s",
                          self._timeout, Message.parse(m, ctx))

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(self._timeout)

        try:
            s.sendto(m, (self.ip, self.port))
        except OSError as ex:
            _LOGGER.error("failed to send msg: %s", ex)
            raise DeviceException from ex

        try:
            data, addr = s.recvfrom(1024)
            m = Message.parse(data, ctx)
            self._device_ts = m.header.value.ts
            if self.debug > 1:
                _LOGGER.debug("recv from %s: %s", addr[0], m)

            self.__id = m.data.value["id"]
            _LOGGER.debug("%s:%s (ts: %s, id: %s) << %s",
                          self.ip, self.port,
                          m.header.value.ts,
                          m.data.value["id"],
                          m.data.value)
            try:
                return m.data.value["result"]
            except KeyError:
                return m.data.value
        except OSError as ex:
            _LOGGER.error("Got error when receiving: %s", ex)
            if retry_count > 0:
                _LOGGER.warning("Retrying with incremented id, "
                                "retries left: %s", retry_count)
                self.__id += 100
                return self.send(command, parameters, retry_count - 1)
            raise DeviceException from ex

    def raw_command(self, cmd, params):
        """Send a raw command to the robot."""
        return self.send(cmd, params)

    def info(self) -> DeviceInfo:
        """Get miIO information from the device."""
        return DeviceInfo(self.send("miIO.info", []))

    @property
    def _id(self) -> int:
        """Increment and return the sequence id."""
        self.__id += 1
        if self.__id >= 9999:
            self.__id = 0
        return self.__id

    @property
    def raw_id(self) -> int:
        """Return the sequence id."""
        return self.__id
