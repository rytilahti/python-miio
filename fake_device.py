import socket
from miio.protocol import Message
from time import time
import datetime
import binascii
import calendar
import binascii
import struct
import logging

_LOGGER = logging.getLogger(__name__)


def run(device_id, token, callback, address="0.0.0.0"):
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
    sock.bind((address, 54321))
    _LOGGER.info(
        "fake miio device started with  address=%s device_id=%s callback=%s token=****",
        address,
        device_id,
        callback,
    )

    while True:
        data, [host, port] = sock.recvfrom(1024)
        if data == helobytes:
            _LOGGER.debug("%s:%s=>PING", host, port)
            m = build_ack(device_id)
            sock.sendto(m, (host, port))
            _LOGGER.debug("%s:%s<=ACK(device_id=%s)", host, port, device_id)
        else:
            request = Message.parse(data, token=token)
            value = request.data.value
            _LOGGER.debug("%s:%s=>%s", host, port, value)
            action, device_call_id = value["method"].split("_")
            source_device_id = (
                f"lumi.{device_call_id}"  #  All known devices use lumi. prefix
            )
            callback(source_device_id, action, value["params"])
            result = {"result": 0, "id": value["id"]}
            header = {
                "length": 0,
                "unknown": 0,
                "device_id": device_id,
                "ts": datetime.datetime.now(),
            }
            msg = {
                "data": {"value": result},
                "header": {"value": header},
                "checksum": 0,
            }
            m = Message.build(msg, token=token)
            _LOGGER.debug("%s:%s<=%s", host, port, result)
            sock.sendto(m, (host, port))


if __name__ == "__main__":

    def callback(source_device, action, params):
        _LOGGER.debug(f"CALLBACK {source_device}=>{action}({params})")

    from miio.gateway_scripts import tokens, fake_device_id

    logging.basicConfig(level="DEBUG")

    device_id = int(fake_device_id)
    device_token = bytes.fromhex(tokens["real"])
    run(device_id, device_token, callback)
