import codecs
import datetime
import socket
import logging
from typing import Any, List

from .protocol import Message

_LOGGER = logging.getLogger(__name__)


class DeviceException(Exception):
    pass


class Device:
    def __init__(self, ip: str, token: str,
                 start_id: int=0, debug: int=0) -> None:
        self.ip = ip
        self.port = 54321
        self.token = bytes.fromhex(token)
        self.debug = debug

        self._timeout = 5
        self._device_ts = None  # type: datetime.datetime
        self.__id = start_id
        self._devtype = None
        self._serial = None

    def do_discover(self):
        """Does a discover to fetch the devtype and serial."""
        m = Device.discover(self.ip)
        if m is not None:
            self._devtype = m.header.value.devtype
            self._serial = m.header.value.serial
            self._device_ts = m.header.value.ts
            if self.debug > 1:
                _LOGGER.debug(m)
            _LOGGER.debug("Discovered %s %s with ts: %s" % (self._devtype,
                                                            self._serial,
                                                            self._device_ts))
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
        for _i in range(3):
            s.sendto(helobytes, (addr, 54321))
        while True:
            try:
                data, addr = s.recvfrom(1024)
                m = Message.parse(data)  # type: Message
                # _LOGGER.debug("Got a response: %s" % m)
                if not is_broadcast:
                    return m

                if addr[0] not in seen_addrs:
                    _LOGGER.info("  IP %s: %s - token: %s" % (
                        addr[0],
                        m.header.value.devtype,
                        codecs.encode(m.checksum, 'hex')))
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

        if parameters:
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
        _LOGGER.debug("%s:%s >>: %s" % (self.ip, self.port, cmd))
        if self.debug > 1:
            _LOGGER.debug("send (timeout %s): %s",
                          self._timeout, Message.parse(m, ctx))

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(self._timeout)

        try:
            s.sendto(m, (self.ip, self.port))
        except OSError as ex:
            _LOGGER.error("failed to send msg: %s" % ex)
            raise DeviceException from ex

        try:
            data, addr = s.recvfrom(1024)
            m = Message.parse(data, ctx)
            self._device_ts = m.header.value.ts
            if self.debug > 1:
                _LOGGER.debug("recv: %s" % m)

            self.__id = m.data.value["id"]
            _LOGGER.debug("%s:%s (ts: %s, id: %s) << %s" % (self.ip, self.port,
                                                            m.header.value.ts,
                                                            m.data.value["id"],
                                                            m.data.value))
            return m.data.value["result"]
        except OSError as ex:
            _LOGGER.error("Got error when receiving: %s", ex)
            if retry_count > 0:
                _LOGGER.warning("Retrying with incremented id, retries left: %s" % retry_count)
                self.__id += 100
                return self.send(command, parameters, retry_count-1)
            raise DeviceException from ex

    @property
    def _id(self) -> int:
        """Returns running id."""
        self.__id += 1
        if self.__id >= 9999:
            self.__id = 0
        return self.__id

    @property
    def raw_id(self) -> int:
        return self.__id
