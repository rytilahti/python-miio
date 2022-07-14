import calendar
import datetime
import logging
import struct

from ..protocol import Message

_LOGGER = logging.getLogger(__name__)

HELO_BYTES = bytes.fromhex(
    "21310020ffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
)


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
            ">HHIII16s", 0x2131, 32, 0, self.server.server_id, timestamp, bytes(16)
        )

    def connection_made(self, transport):
        """Set the transport."""
        self.transport = transport
        self._connected = True
        _LOGGER.info(
            "Miio push server started with address=%s server_id=%s",
            self.server._address,
            self.server.server_id,
        )

    def connection_lost(self, exc):
        """Handle connection lost."""
        if self._connected:
            _LOGGER.error("Connection unexpectedly lost in Miio push server: %s", exc)

    def send_ping_ACK(self, host, port):
        _LOGGER.debug("%s:%s=>PING", host, port)
        m = self._build_ack()
        self.transport.sendto(m, (host, port))
        _LOGGER.debug("%s:%s<=ACK(server_id=%s)", host, port, self.server.server_id)

    def send_msg_OK(self, host, port, msg_id, token):
        # This result means OK, but some methods return ['ok'] instead of 0
        # might be necessary to use different results for different methods
        result = {"result": 0, "id": msg_id}
        header = {
            "length": 0,
            "unknown": 0,
            "device_id": self.server.server_id,
            "ts": datetime.datetime.now(),
        }
        msg = {
            "data": {"value": result},
            "header": {"value": header},
            "checksum": 0,
        }
        response = Message.build(msg, token=token)
        self.transport.sendto(response, (host, port))
        _LOGGER.debug(">> %s:%s: %s", host, port, result)

    def datagram_received(self, data, addr):
        """Handle received messages."""
        try:
            (host, port) = addr
            if data == HELO_BYTES:
                self.send_ping_ACK(host, port)
                return

            if host not in self.server._registered_devices:
                _LOGGER.warning(
                    "Datagram received from unknown device (%s:%s)",
                    host,
                    port,
                )
                return

            token = self.server._registered_devices[host]["token"]
            callback = self.server._registered_devices[host]["callback"]

            msg = Message.parse(data, token=token)
            msg_value = msg.data.value
            msg_id = msg_value["id"]
            _LOGGER.debug("<< %s:%s: %s", host, port, msg_value)

            # Parse message
            action, device_call_id = msg_value["method"].rsplit(":", 1)
            source_device_id = device_call_id.replace("_", ".")

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
        self._sock.close()
        _LOGGER.info("Miio push server stopped")
