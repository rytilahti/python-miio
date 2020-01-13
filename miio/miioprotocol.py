"""miIO protocol implementation

This module contains the implementation of routines to send handshakes, send
commands and discover devices (MiIOProtocol).
"""
import binascii
import codecs
import datetime
import logging
import socket
from typing import Any, List

import construct

from .exceptions import DeviceError, DeviceException, RecoverableError
from .protocol import Message

_LOGGER = logging.getLogger(__name__)


class MiIOProtocol:
    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
    ) -> None:
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
            token = 32 * "0"
        if token is not None:
            self.token = bytes.fromhex(token)
        self.debug = debug
        self.lazy_discover = lazy_discover

        self._timeout = 5
        self._discovered = False
        self._device_ts = None  # type: datetime.datetime
        self.__id = start_id
        self._device_id = None

    def send_handshake(self) -> Message:
        """Send a handshake to the device,
        which can be used to the device type and serial.
        The handshake must also be done regularly to enable communication
        with the device.

        :rtype: Message

        :raises DeviceException: if the device could not be discovered."""
        m = MiIOProtocol.discover(self.ip)
        if m is not None:
            self._device_id = m.header.value.device_id
            self._device_ts = m.header.value.ts
            self._discovered = True
            if self.debug > 1:
                _LOGGER.debug(m)
            _LOGGER.debug(
                "Discovered %s with ts: %s, token: %s",
                binascii.hexlify(self._device_id).decode(),
                self._device_ts,
                codecs.encode(m.checksum, "hex"),
            )
        else:
            _LOGGER.error("Unable to discover a device at address %s", self.ip)
            raise DeviceException("Unable to discover the device %s" % self.ip)

        return m

    @staticmethod
    def discover(addr: str = None) -> Any:
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
            addr = "<broadcast>"
            is_broadcast = True
            _LOGGER.info("Sending discovery to %s with timeout of %ss..", addr, timeout)
        # magic, length 32
        helobytes = bytes.fromhex(
            "21310020ffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
        )

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
                    _LOGGER.info(
                        "  IP %s (ID: %s) - token: %s",
                        addr[0],
                        binascii.hexlify(m.header.value.device_id).decode(),
                        codecs.encode(m.checksum, "hex"),
                    )
                    seen_addrs.append(addr[0])
            except socket.timeout:
                if is_broadcast:
                    _LOGGER.info("Discovery done")
                return  # ignore timeouts on discover
            except Exception as ex:
                _LOGGER.warning("error while reading discover results: %s", ex)
                break

    def send(self, command: str, parameters: Any = None, retry_count=3) -> Any:
        """Build and send the given command.
        Note that this will implicitly call :func:`send_handshake` to do a handshake,
        and will re-try in case of errors while incrementing the `_id` by 100.

        :param str command: Command to send
        :param dict parameters: Parameters to send, or an empty list FIXME
        :param retry_count: How many times to retry in case of failure
        :raises DeviceException: if an error has occurred during communication."""

        if not self.lazy_discover or not self._discovered:
            self.send_handshake()

        cmd = {"id": self._id, "method": command}

        if parameters is not None:
            cmd["params"] = parameters
        else:
            cmd["params"] = []

        send_ts = self._device_ts + datetime.timedelta(seconds=1)
        header = {
            "length": 0,
            "unknown": 0x00000000,
            "device_id": self._device_id,
            "ts": send_ts,
        }

        msg = {"data": {"value": cmd}, "header": {"value": header}, "checksum": 0}
        m = Message.build(msg, token=self.token)
        _LOGGER.debug("%s:%s >>: %s", self.ip, self.port, cmd)
        if self.debug > 1:
            _LOGGER.debug(
                "send (timeout %s): %s",
                self._timeout,
                Message.parse(m, token=self.token),
            )

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
            _LOGGER.debug(
                "%s:%s (ts: %s, id: %s) << %s",
                self.ip,
                self.port,
                m.header.value.ts,
                m.data.value["id"],
                m.data.value,
            )
            if "error" in m.data.value:
                error = m.data.value["error"]
                if "code" in error and error["code"] == -30001:
                    raise RecoverableError(error)
                raise DeviceError(error)

            try:
                return m.data.value["result"]
            except KeyError:
                return m.data.value
        except construct.core.ChecksumError as ex:
            raise DeviceException(
                "Got checksum error which indicates use "
                "of an invalid token. "
                "Please check your token!"
            ) from ex
        except OSError as ex:
            if retry_count > 0:
                _LOGGER.debug(
                    "Retrying with incremented id, retries left: %s", retry_count
                )
                self.__id += 100
                self._discovered = False
                return self.send(command, parameters, retry_count - 1)

            _LOGGER.error("Got error when receiving: %s", ex)
            raise DeviceException("No response from the device") from ex

        except RecoverableError as ex:
            if retry_count > 0:
                _LOGGER.debug(
                    "Retrying to send failed command, retries left: %s", retry_count
                )
                return self.send(command, parameters, retry_count - 1)

            _LOGGER.error("Got error when receiving: %s", ex)
            raise DeviceException("Unable to recover failed command") from ex

    @property
    def _id(self) -> int:
        """Increment and return the sequence id."""
        self.__id += 1
        if self.__id >= 9999:
            self.__id = 1
        return self.__id

    @property
    def raw_id(self):
        return self.__id
