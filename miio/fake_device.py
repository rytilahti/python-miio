import socket
from miio.protocol import Message
import datetime
import calendar
import struct
import logging

_LOGGER = logging.getLogger(__name__)


class FakeDevice:
    _device_id = None
    _address = None
    _token = None

    def __init__(self, device_id, token, address="0.0.0.0"):
        self._device_id = device_id
        self._token = token
        self._address = address

    def run(self, callback):
        def build_ack(device: int):
            # Iriginal devices are using year 1970, but it seems current datetime is fine
            timestamp = calendar.timegm(datetime.datetime.now().timetuple())
            # ACK packet not signed, 16 bytes header + 16 bytes of zeroes
            return struct.pack(">HHIII16s", 0x2131, 32, 0, device, timestamp, bytes(16))

        helobytes = bytes.fromhex(
            "21310020ffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
        )

        sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        # Gateway interacts only with port 54321
        sock.bind((self._address, 54321))
        _LOGGER.info(
            "fake miio device started with  address=%s device_id=%s callback=%s token=****",
            self._address,
            self._device_id,
            callback,
        )

        while True:
            data, [host, port] = sock.recvfrom(1024)
            if data == helobytes:
                _LOGGER.debug("%s:%s=>PING", host, port)
                m = build_ack(self._device_id)
                sock.sendto(m, (host, port))
                _LOGGER.debug("%s:%s<=ACK(device_id=%s)", host, port, self._device_id)
            else:
                request = Message.parse(data, token=self._token)
                value = request.data.value
                _LOGGER.debug("%s:%s=>%s", host, port, value)
                action, device_call_id = value["method"].split("_")
                source_device_id = (
                    f"lumi.{device_call_id}"  # All known devices use lumi. prefix
                )
                callback(source_device_id, action, value["params"])
                result = {"result": 0, "id": value["id"]}
                header = {
                    "length": 0,
                    "unknown": 0,
                    "device_id": self._device_id,
                    "ts": datetime.datetime.now(),
                }
                msg = {
                    "data": {"value": result},
                    "header": {"value": header},
                    "checksum": 0,
                }
                response = Message.build(msg, token=self._token)
                _LOGGER.debug("%s:%s<=%s", host, port, result)
                sock.sendto(response, (host, port))


if __name__ == "__main__":

    def callback(source_device, action, params):
        _LOGGER.debug(f"CALLBACK {source_device}=>{action}({params})")

    from gateway_scripts import tokens, fake_device_id

    logging.basicConfig(level="DEBUG")

    device_id = int(fake_device_id)
    device_token = bytes.fromhex(tokens["real"])
    fake_device = FakeDevice(device_id, device_token)
    fake_device.run(callback)
