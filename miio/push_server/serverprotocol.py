import calendar
import datetime
import logging
import struct

from ..protocol import Message

_LOGGER = logging.getLogger(__name__)

HELO_BYTES = bytes.fromhex(
    "21310020ffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
)

ERR_INVALID = -1
ERR_UNSUPPORTED = -2
ERR_METHOD_EXEC_FAILED = -3


class ServerProtocol:
    """Handle responding to UDP packets."""

    def __init__(self, loop, udp_socket, server):
        """Initialize the class."""
        self.transport = None
        self._loop = loop
        self._sock = udp_socket
        self.server = server
        self._connected = False

    def _build_ack(self):
        # Original devices are using year 1970, but it seems current datetime is fine
        timestamp = calendar.timegm(datetime.datetime.now().timetuple())
        # ACK packet not signed, 16 bytes header + 16 bytes of zeroes
        return struct.pack(
            ">HHIII16s", 0x2131, 32, 0, self.server.device_id, timestamp, bytes(16)
        )

    def connection_made(self, transport):
        """Set the transport."""
        self.transport = transport
        self._connected = True
        _LOGGER.info(
            "Miio push server started with address=%s server_id=%s",
            self.server._address,
            self.server.device_id,
        )

    def connection_lost(self, exc):
        """Handle connection lost."""
        if self._connected:
            _LOGGER.error("Connection unexpectedly lost in Miio push server: %s", exc)

    def send_ping_ACK(self, host, port):
        _LOGGER.debug("%s:%s=>PING", host, port)
        m = self._build_ack()
        self.transport.sendto(m, (host, port))
        _LOGGER.debug("%s:%s<=ACK(server_id=%s)", host, port, self.server.device_id)

    def _create_message(self, data, token, device_id):
        """Create a message to be sent to the client."""
        header = {
            "length": 0,
            "unknown": 0,
            "device_id": device_id,
            "ts": datetime.datetime.now(),
        }
        msg = {
            "data": {"value": data},
            "header": {"value": header},
            "checksum": 0,
        }
        response = Message.build(msg, token=token)

        return response

    def send_response(self, host, port, msg_id, token, payload=None):
        if payload is None:
            payload = {}

        data = {**payload, "id": msg_id}
        msg = self._create_message(data, token, device_id=self.server.device_id)

        self.transport.sendto(msg, (host, port))
        _LOGGER.debug(">> %s:%s: %s", host, port, data)

    def send_error(self, host, port, msg_id, token, code, message):
        """Send error message with given code and message to the client."""
        return self.send_response(
            host, port, msg_id, token, {"error": {"code": code, "error": message}}
        )

    def _handle_datagram_from_registered_device(self, host, port, data):
        """Handle requests from registered eventing devices."""
        token = self.server._registered_devices[host]["token"]
        callback = self.server._registered_devices[host]["callback"]

        msg = Message.parse(data, token=token)
        msg_value = msg.data.value
        msg_id = msg_value["id"]
        _LOGGER.debug("<< %s:%s: %s", host, port, msg_value)

        # Send OK
        # This result means OK, but some methods return ['ok'] instead of 0
        # might be necessary to use different results for different methods
        payload = {"result": 0}
        self.send_response(host, port, msg_id, token, payload=payload)

        # Parse message
        action, device_call_id = msg_value["method"].rsplit(":", 1)
        source_device_id = device_call_id.replace("_", ".")

        callback(source_device_id, action, msg_value.get("params"))

    def _handle_datagram_from_client(self, host: str, port: int, data):
        """Handle datagram from a regular client."""
        token = bytes.fromhex(32 * "0")  # TODO: make token configurable?
        msg = Message.parse(data, token=token)
        msg_value = msg.data.value
        msg_id = msg_value["id"]

        _LOGGER.debug(
            "Received datagram #%s from regular client: %s: %s",
            msg_id,
            host,
            msg_value,
        )

        if "method" not in msg_value:
            return self.send_error(
                host, port, msg_id, token, ERR_INVALID, "missing method"
            )

        methods = self.server.methods
        if msg_value["method"] not in methods:
            return self.send_error(
                host, port, msg_id, token, ERR_UNSUPPORTED, "unsupported method"
            )

        _LOGGER.debug("Got method call: %s", msg_value["method"])
        method = methods[msg_value["method"]]
        if callable(method):
            try:
                response = method(msg_value)
            except Exception as ex:
                _LOGGER.exception(ex)
                return self.send_error(
                    host,
                    port,
                    msg_id,
                    token,
                    ERR_METHOD_EXEC_FAILED,
                    f"Exception {type(ex)}: {ex}",
                )
        else:
            response = method

        _LOGGER.debug("Responding %s with %s", msg_id, response)
        return self.send_response(host, port, msg_id, token, payload=response)

    def datagram_received(self, data, addr):
        """Handle received messages."""
        try:
            (host, port) = addr
            if data == HELO_BYTES:
                return self.send_ping_ACK(host, port)

            if host in self.server._registered_devices:
                return self._handle_datagram_from_registered_device(host, port, data)
            else:
                return self._handle_datagram_from_client(host, port, data)

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
        self._sock.close()
        _LOGGER.info("Miio push server stopped")
