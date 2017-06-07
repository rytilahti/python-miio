import codecs
import datetime
import time
import socket
import logging

from mirobo import Utils, Message

_LOGGER = logging.getLogger(__name__)

class DeviceException(Exception):
    pass


class Device:
    def __init__(self, ip, token, debug=0):
        self.ip = ip
        self.port = 54321
        self.token = bytes.fromhex(token)
        self.debug = debug

        self._timeout = 5
        self.__id = 0
        self._devtype = None
        self._serial = None
        self._ts = None
        self._ts_server = int(time.mktime(datetime.datetime.utcnow().timetuple()))

    def __enter__(self):
        """Does a discover to fetch the devtype and serial."""
        m = Device.discover(self.ip)
        if m is not None:
            self._devtype = m.header.value.devtype
            self._serial = m.header.value.serial
            self._ts = m.header.value.ts
            self._ts_server = int(time.mktime(datetime.datetime.utcnow().timetuple()))
        else:
            _LOGGER.error("Unable to discover a device at address %s", self.ip)

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @staticmethod
    def discover(addr=None):
        """Scan for devices in the network."""
        timeout = 5
        is_broadcast = addr is None
        seen_addrs = []
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
        for i in range(3):
            s.sendto(helobytes, (addr, 54321))
        while True:
            try:
                data, addr = s.recvfrom(1024)
                m = Message.parse(data)
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

    def send(self, command, parameters=None):
        """Build and send the given command."""
        delta_ts = int(time.mktime(datetime.datetime.utcnow().timetuple())) - self._ts_server
        if self._devtype is None or self._serial is None or (delta_ts > 120):
            self.__enter__()  # when called outside of cm, initialize.
            delta_ts = int(time.mktime(datetime.datetime.utcnow().timetuple())) - self._ts_server

        cmd = {
            "id": self._id,
            "method": command,
        }

        if parameters:
            cmd["params"] = parameters

        self._ts += datetime.timedelta(seconds = delta_ts)
        header = {'length': 0, 'unknown': 0x00000000,
                  'devtype': self._devtype, 'serial': self._serial,
                  'ts': self._ts}

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
            if self.debug > 1:
                _LOGGER.debug("recv: %s" % m)
            _LOGGER.debug("%s:%s (ts: %s) << %s" % (self.ip, self.port,
                                                    m.header.value.ts,
                                                    m.data.value))
            self._ts = m.header.value.ts
            self._ts_server = int(time.mktime(datetime.datetime.utcnow().timetuple()))
            return m.data.value["result"]
        except OSError as ex:
            _LOGGER.error("got error when receiving: %s", ex)
            raise DeviceException from ex

    @property
    def _id(self):
        """Returns running id."""
        self.__id += 1
        return self.__id