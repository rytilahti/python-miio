import logging
import socket
import datetime
import codecs
from mirobo import (Message, Utils, VacuumStatus, ConsumableStatus,
                    CleaningSummary, CleaningDetails, Timer)

_LOGGER = logging.getLogger(__name__)


class VacuumException(Exception):
    pass


class Vacuum:
    """Main class representing the vacuum."""
    def __init__(self, ip, token, debug=0):
        self.ip = ip
        self.port = 54321
        self.token = bytes.fromhex(token)
        self.debug = debug

        # TODO this is a mess, find a nicer way to provide token to construct
        Utils.token = self.token
        self._timeout = 5
        self.__id = 0
        self._devtype = None
        self._serial = None

    def __enter__(self):
        """Does a discover to fetch the devtype and serial."""
        m = Vacuum.discover(self.ip)
        if m is not None:
            self._devtype = m.header.value.devtype
            self._serial = m.header.value.serial
        else:
            _LOGGER.error("Unable to discover a device at address %s", self.ip)

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @property
    def _id(self):
        """Returns running id."""
        self.__id += 1
        return self.__id

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
        if self._devtype is None or self._serial is None:
            self.__enter__()  # when called outside of cm, initialize.

        cmd = {
            "id": self._id,
            "method": command,
        }

        if parameters:
            cmd["params"] = parameters

        header = {'length': 0, 'unknown': 0x00000000,
                  'devtype': self._devtype, 'serial': self._serial,
                  'ts': datetime.datetime.utcnow()}

        msg = {'data': {'value': cmd},
               'header': {'value': header},
               'checksum': 0}
        m = Message.build(msg)
        _LOGGER.debug("%s:%s >>: %s" % (self.ip, self.port, cmd))
        if self.debug > 1:
            _LOGGER.debug("send (timeout %s): %s",
                          self._timeout, Message.parse(m))

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(self._timeout)

        try:
            s.sendto(m, (self.ip, self.port))
        except OSError as ex:
            _LOGGER.error("failed to send msg: %s" % ex)
            raise VacuumException from ex

        try:
            data, addr = s.recvfrom(1024)
            m = Message.parse(data)
            if self.debug > 1:
                _LOGGER.debug("recv: %s" % m)
            _LOGGER.debug("%s:%s (ts: %s) << %s" % (self.ip, self.port,
                                                    m.header.value.ts,
                                                    m.data.value))
            return m.data.value["result"]
        except OSError as ex:
            _LOGGER.error("got error when receiving: %s", ex)
            raise VacuumException from ex

    def start(self):
        return self.send("app_start")

    def stop(self):
        return self.send("app_stop")

    def spot(self):
        return self.send("app_spot")

    def pause(self):
        return self.send("app_pause")

    def home(self):
        self.send("app_stop")
        return self.send("app_charge")

    def status(self):
        return VacuumStatus(self.send("get_status")[0])

    def log_upload_status(self):
        # {"result": [{"log_upload_status": 7}], "id": 1}
        return self.send("get_log_upload_status")

    def consumable_status(self):
        return ConsumableStatus(self.send("get_consumable")[0])

    def map(self):
        # returns ['retry'] without internet
        return self.send("get_map_v1")

    def clean_history(self):
        return CleaningSummary(self.send("get_clean_summary"))

    def clean_details(self, id_):
        details = self.send("get_clean_record", [id_])

        res = list()
        for rec in details:
            res.append(CleaningDetails(rec))

        return res

    def find(self):
        return self.send("find_me", [""])

    def timer(self):
        timers = list()
        for rec in self.send("get_timer", [""]):
            timers.append(Timer(rec))

        return timers

    def set_timer(self, details):
        # how to create timers/change values?
        # ['ts', 'on'] to enable
        raise NotImplementedError()
        return self.send("upd_timer", ["ts", "on"])

    def dnd_status(self):
        # {'result': [{'enabled': 1, 'start_minute': 0, 'end_minute': 0,
        #  'start_hour': 22, 'end_hour': 8}], 'id': 1}
        return self.send("get_dnd_timer")

    def set_dnd(self, start_hr, start_min, end_hr, end_min):
        return self.send("set_dnd_timer",
                         [start_hr, start_min, end_hr, end_min])

    def disable_dnd(self):
        return self.send("close_dnd_timer", [""])

    def set_fan_speed(self, speed):
        # speed = [38, 60 or 77]
        return self.send("set_custom_mode", [speed])

    def fan_speed(self):
        return self.send("get_custom_mode")[0]

    def raw_command(self, cmd, params):
        return self.send(cmd, params)
