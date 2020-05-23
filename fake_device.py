import socket
from miio.protocol import Message, TimeAdapter, EncryptionAdapter, Utils
from time import time
import datetime
import binascii
import calendar
import binascii
import struct


def run_server(device_id, token, callbacks, address="0.0.0.0"):
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

    while True:
        data, [host, port] = sock.recvfrom(1024)
        if data == helobytes:
            print(f"{host}:{port}=>PING")
            m = build_ack(device_id)
            sock.sendto(m, (host, port))
            print(f"{host}:{port}<=ACK(device_id={device_id})")
        else:
            print(f"{host}:{port}=>{request.data.value}")
            request = Message.parse(data, token=token)
            value = request.data.value
            result = callbacks[value["method"]](value["id"], value["params"])
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
            print(f"{host}:{port}<={result}")
            sock.sendto(m, (host, port))


callbacks = {
    "set_fm_volume": lambda id, params: {"result": ["ok"], "id": id},
    "set_usb_on": lambda id, params: {"result": 0, "id": id},
    "move": lambda id, params: {"result": 0, "id": id},
    "rotate": lambda id, params: {"result": 0, "id": id},
}

device_id = 120009025
device_token = bytes.fromhex("9bc7c7ce6291d3e443fd7708608b9892")
run_server(device_id, device_token, callbacks)
