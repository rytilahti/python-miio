import asyncio
import calendar
import datetime
import logging
import socket
import struct
from json import dumps
from random import randint

from ..protocol import Message

_LOGGER = logging.getLogger(__name__)

SERVER_PORT = 54321
FAKE_DEVICE_ID = "120009025"
FAKE_DEVICE_MODEL = "chuangmi.plug.v3"
HELO_BYTES = bytes.fromhex(
    "21310020ffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
)


def construct_script(  # nosec
    script_id,
    action,
    extra,
    source_sid,
    source_model,
    target_id,
    target_ip,
    target_model,
    token_enc,
    message_id=0,
    event=None,
    command_extra="",
    trigger_value=None,
    trigger_token="",
):
    if event is None:
        event = action

    if source_sid.startswith("lumi."):
        lumi, source_id = source_sid.split(".")
    else:
        source_id = source_sid

    script = [
        [
            script_id,
            [
                "1.0",
                randint(1590161094, 1590162094),  # nosec
                [
                    "0",
                    {
                        "did": source_sid,
                        "extra": extra,
                        "key": "event." + source_model + "." + event,
                        "model": source_model,
                        "src": "device",
                        "timespan": ["0 0 * * 0,1,2,3,4,5,6", "0 0 * * 0,1,2,3,4,5,6"],
                        "token": trigger_token,
                    },
                ],
                [
                    {
                        "command": target_model + "." + action + "_" + source_id,
                        "did": str(target_id),
                        "extra": command_extra,
                        "id": message_id,
                        "ip": target_ip,
                        "model": target_model,
                        "token": token_enc,
                        "value": "",
                    }
                ],
            ],
        ]
    ]

    if trigger_value is not None:
        script[0][1][2][1]["value"] = trigger_value

    script_data = dumps(script, separators=(",", ":"))

    return script_data


class PushServer:
    """Async UDP push server using a fake miio device registered to a real gateway."""

    def __init__(self, gateway_ip):
        """Initialize the class."""
        self._gateway_ip = gateway_ip

        self._address = "0.0.0.0"  # nosec
        self._device_ip = None
        self._device_id = int(FAKE_DEVICE_ID)
        self._device_model = FAKE_DEVICE_MODEL

        self._listen_couroutine = None
        self._registered_callbacks = {}

    def _create_udp_server(self):
        """Create the UDP socket and protocol."""
        udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        # Gateway interacts only with port 54321
        udp_socket.bind((self._address, SERVER_PORT))

        # Connect to the gateway to get device_ip
        udp_socket.connect((self._gateway_ip, SERVER_PORT))
        self._device_ip = udp_socket.getsockname()[0]
        _LOGGER.debug("Miio push server device ip=%s", self._device_ip)

        loop = asyncio.get_event_loop()

        return loop.create_datagram_endpoint(
            lambda: self.ServerProtocol(loop, udp_socket, self),
            sock=udp_socket,
        )

    def Register_gateway(self, ip, token, callback):
        """Register a gateway to this push server."""
        if ip in self._registered_callbacks:
            _LOGGER.error(
                "A callback for ip '%s' was already registed, overwriting previous callback",
                ip,
            )
        self._registered_callbacks[ip] = {
            "callback": callback,
            "token": bytes.fromhex(token),
        }

    def Unregister_gateway(self, ip):
        """Unregister a gateway from this push server."""
        if ip in self._registered_callbacks:
            self._registered_callbacks.pop(ip)

    async def Start_server(self):
        """Start Miio push server."""
        if self._listen_couroutine is not None:
            _LOGGER.error("Miio push server already started, not starting another one.")
            return

        listen_task = self._create_udp_server()
        _, self._listen_couroutine = await listen_task

    def Stop_server(self):
        """Stop Miio push server."""
        if self._listen_couroutine is None:
            return

        self._listen_couroutine.close()
        self._listen_couroutine = None

    @property
    def device_ip(self):
        """Return the IP of the device running this server."""
        return self._device_ip

    @property
    def device_id(self):
        """Return the ID of the fake device beeing emulated."""
        return self._device_id

    @property
    def device_model(self):
        """Return the model of the fake device beeing emulated."""
        return self._device_model

    class ServerProtocol:
        """Handle responding to UDP packets."""

        def __init__(self, loop, udp_socket, parent):
            """Initialize the class."""
            self.transport = None
            self._loop = loop
            self._sock = udp_socket
            self.parent = parent
            self._connected = False

        def _build_ack(self):
            # Original devices are using year 1970, but it seems current datetime is fine
            timestamp = calendar.timegm(datetime.datetime.now().timetuple())
            # ACK packet not signed, 16 bytes header + 16 bytes of zeroes
            return struct.pack(
                ">HHIII16s", 0x2131, 32, 0, self.parent._device_id, timestamp, bytes(16)
            )

        def connection_made(self, transport):
            """Set the transport."""
            self.transport = transport
            self._connected = True
            _LOGGER.info(
                "Miio push server started with address=%s device_id=%s",
                self.parent._address,
                self.parent._device_id,
            )

        def connection_lost(self, exc):
            """Handle connection lost."""
            if self._connected:
                _LOGGER.error(
                    "Connection unexpectedly lost in Miio push server: %s", exc
                )

        def send_ping_ACK(self, host, port):
            _LOGGER.debug("%s:%s=>PING", host, port)
            m = self._build_ack()
            self.transport.sendto(m, (host, port))
            _LOGGER.debug(
                "%s:%s<=ACK(device_id=%s)", host, port, self.parent._device_id
            )

        def send_msg_OK(self, host, port, msg_id, token):
            # This result means OK, but some methods return ['ok'] instead of 0
            # might be necessary to use different results for different methods
            result = {"result": 0, "id": msg_id}
            header = {
                "length": 0,
                "unknown": 0,
                "device_id": self.parent._device_id,
                "ts": datetime.datetime.now(),
            }
            msg = {
                "data": {"value": result},
                "header": {"value": header},
                "checksum": 0,
            }
            response = Message.build(msg, token=token)
            self.transport.sendto(response, (host, port))
            _LOGGER.debug("%s:%s<=%s", host, port, result)

        def datagram_received(self, data, addr):
            """Handle received messages."""
            try:
                (host, port) = addr
                if data == HELO_BYTES:
                    self.send_ping_ACK(host, port)
                else:
                    if host not in self.parent._registered_callbacks:
                        _LOGGER.info(
                            "Push message received from unknown Miio device with ip %s:%s",
                            host,
                            port,
                        )
                        return
                    token = self.parent._registered_callbacks[host]["token"]
                    callback = self.parent._registered_callbacks[host]["callback"]

                    msg = Message.parse(data, token=token)
                    msg_value = msg.data.value
                    msg_id = msg_value["id"]
                    _LOGGER.debug("%s:%s=>%s", host, port, msg_value)

                    # Parse message
                    action, device_call_id = msg_value["method"].rsplit("_", 1)
                    source_device_id = (
                        f"lumi.{device_call_id}"  # All known devices use lumi. prefix
                    )

                    callback(source_device_id, action, msg_value.get("params"))

                    # Send OK
                    self.send_msg_OK(host, port, msg_id, token)

            except Exception:
                _LOGGER.exception(
                    "Cannot process Miio push server packet: '%s' from %s:%s",
                    data,
                    host,
                    port,
                )

        def error_received(self, exc):
            """Log UDP errors."""
            _LOGGER.error("UDP error received in Miio push server: %s", exc)

        def close(self):
            """Stop the server."""
            _LOGGER.debug("Miio push server shutting down")
            self._connected = False
            if self.transport:
                self.transport.close()
            self._loop.remove_writer(self._sock.fileno())
            self._loop.remove_reader(self._sock.fileno())
            self._sock.close()
            _LOGGER.info("Miio push server stopped")
