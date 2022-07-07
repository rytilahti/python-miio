import asyncio
import calendar
import datetime
import logging
import socket
import struct
from json import dumps
from random import randint
from typing import Any, Optional

import attr

from .device import Device
from .protocol import Message, Utils

_LOGGER = logging.getLogger(__name__)

SERVER_PORT = 54321
FAKE_DEVICE_ID = "120009025"
FAKE_DEVICE_MODEL = "chuangmi.plug.v3"
HELO_BYTES = bytes.fromhex(
    "21310020ffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
)


@attr.s(auto_attribs=True)
class EventInfo:
    """Event info to register to the push server."""

    action: str  # user friendly name of the event, can be set arbitrarily and will be received by the server as the name of the event
    extra: str  # the identification of this event, this determines on what event the callback is triggered
    event: Optional[str] = None  # defaults to the action
    command_extra: str = ""
    trigger_value: Optional[Any] = None
    trigger_token: str = ""
    source_sid: Optional[str] = None  # Normally not needed and obtained from device
    source_model: Optional[str] = None  # Normally not needed and obtained from device
    source_token: Optional[str] = None  # Normally not needed and obtained from device


def calculated_token_enc(token):
    token_bytes = bytes.fromhex(token)
    encrypted_token = Utils.encrypt(token_bytes, token_bytes)
    encrypted_token_hex = encrypted_token.hex()
    return encrypted_token_hex[0:32]


class PushServer:
    """Async UDP push server using a fake miio device registered to a real miio
    device."""

    def __init__(self, device_ip):
        """Initialize the class."""
        self._device_ip = device_ip

        self._address = "0.0.0.0"  # nosec
        self._server_ip = None
        self._server_id = int(FAKE_DEVICE_ID)
        self._server_model = FAKE_DEVICE_MODEL

        self._listen_couroutine = None
        self._registered_devices = {}

        self._event_id = 1000000

    async def start(self):
        """Start Miio push server."""
        if self._listen_couroutine is not None:
            _LOGGER.error("Miio push server already started, not starting another one.")
            return

        listen_task = self._create_udp_server()
        _, self._listen_couroutine = await listen_task

    def stop(self):
        """Stop Miio push server."""
        if self._listen_couroutine is None:
            return

        for ip in list(self._registered_devices):
            self.unregister_miio_device(self._registered_devices[ip]["device"])

        self._listen_couroutine.close()
        self._listen_couroutine = None

    def register_miio_device(self, device: Device, callback):
        """Register a miio device to this push server."""
        if device.ip is None:
            _LOGGER.error(
                "Can not register miio device to push server since it has no ip"
            )
            return
        if device.token is None:
            _LOGGER.error(
                "Can not register miio device to push server since it has no token"
            )
            return

        event_ids = []
        if device.ip in self._registered_devices:
            _LOGGER.error(
                "A device for ip '%s' was already registed, overwriting previous callback",
                device.ip,
            )
            event_ids = self._registered_devices[device.ip]["event_ids"]

        self._registered_devices[device.ip] = {
            "callback": callback,
            "token": bytes.fromhex(device.token),
            "event_ids": event_ids,
            "device": device,
        }

    def unregister_miio_device(self, device: Device):
        """Unregister a miio device from this push server."""
        device_info = self._registered_devices.get(device.ip)
        if device_info is None:
            _LOGGER.debug("Device with ip %s not registered, bailing out", device.ip)
            return

        for event_id in device_info["event_ids"]:
            self.unsubscribe_event(device, event_id)
        self._registered_devices.pop(device.ip)
        _LOGGER.debug("push server: unregistered miio device with ip %s", device.ip)

    def subscribe_event(self, device: Device, event_info: EventInfo):
        """Subscribe to a event such that the device will start pushing data for that
        event."""
        if device.ip not in self._registered_devices:
            _LOGGER.error("Can not subscribe event, miio device not yet registered")
            return None

        if self.server_ip is None:
            _LOGGER.error("Can not subscribe event withouth starting the push server")
            return None

        self._event_id = self._event_id + 1
        event_id = f"x.scene.{self._event_id}"

        event_payload = self._construct_event(event_id, event_info, device)

        response = device.send(
            "send_data_frame",
            {
                "cur": 0,
                "data": event_payload,
                "data_tkn": 29576,
                "total": 1,
                "type": "scene",
            },
        )

        if response != ["ok"]:
            _LOGGER.error(
                "Error subscribing event, response %s, event_payload %s",
                response,
                event_payload,
            )
            return None

        event_ids = self._registered_devices[device.ip]["event_ids"]
        event_ids.append(event_id)

        return event_id

    def unsubscribe_event(self, device: Device, event_id):
        """Unsubscribe from a event by id."""
        result = device.send("miIO.xdel", [event_id])
        if result == ["ok"]:
            event_ids = self._registered_devices[device.ip]["event_ids"]
            if event_id in event_ids:
                event_ids.remove(event_id)
        else:
            _LOGGER.error("Error removing event_id %s: %s", event_id, result)

        return result

    def _get_server_ip(self):
        """Connect to the miio device to get server_ip using a one time use socket."""
        get_ip_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        get_ip_socket.bind((self._address, SERVER_PORT))
        get_ip_socket.connect((self._device_ip, SERVER_PORT))
        server_ip = get_ip_socket.getsockname()[0]
        get_ip_socket.close()
        _LOGGER.debug("Miio push server device ip=%s", server_ip)
        return server_ip

    def _create_udp_server(self):
        """Create the UDP socket and protocol."""
        self._server_ip = self._get_server_ip()

        # Create a fresh socket that will be used for the push server
        udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        udp_socket.bind((self._address, SERVER_PORT))

        loop = asyncio.get_event_loop()

        return loop.create_datagram_endpoint(
            lambda: self.ServerProtocol(loop, udp_socket, self),
            sock=udp_socket,
        )

    def _construct_event(  # nosec
        self,
        event_id,
        info: EventInfo,
        device: Device,
    ):
        """Construct the event data payload needed to subscribe to an event."""
        if info.event is None:
            info.event = info.action
        if info.source_sid is None:
            info.source_sid = str(device.device_id)
        if info.source_model is None:
            info.source_model = device.model
        if info.source_token is None:
            info.source_token = device.token

        token_enc = calculated_token_enc(info.source_token)
        source_id = info.source_sid.replace(".", "_")
        command = f"{self.server_model}.{info.action}:{source_id}"
        key = f"event.{info.source_model}.{info.event}"
        message_id = 0

        if len(command) > 49:
            _LOGGER.error(
                "push server event command can be max 49 chars long, '%s' is %i chars",
                command,
                len(command),
            )

        trigger_data = {
            "did": info.source_sid,
            "extra": info.extra,
            "key": key,
            "model": info.source_model,
            "src": "device",
            "timespan": [
                "0 0 * * 0,1,2,3,4,5,6",
                "0 0 * * 0,1,2,3,4,5,6",
            ],
            "token": info.trigger_token,
        }

        target_data = {
            "command": command,
            "did": str(self.server_id),
            "extra": info.command_extra,
            "id": message_id,
            "ip": self.server_ip,
            "model": self.server_model,
            "token": token_enc,
            "value": "",
        }

        event_data = [
            [
                event_id,
                [
                    "1.0",
                    randint(1590161094, 1590162094),  # nosec
                    [
                        "0",
                        trigger_data,
                    ],
                    [target_data],
                ],
            ]
        ]

        if info.trigger_value is not None:
            event_data[0][1][2][1]["value"] = info.trigger_value

        event_payload = dumps(event_data, separators=(",", ":"))

        return event_payload

    @property
    def server_ip(self):
        """Return the IP of the device running this server."""
        return self._server_ip

    @property
    def server_id(self):
        """Return the ID of the fake device beeing emulated."""
        return self._server_id

    @property
    def server_model(self):
        """Return the model of the fake device beeing emulated."""
        return self._server_model

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
                ">HHIII16s", 0x2131, 32, 0, self.parent.server_id, timestamp, bytes(16)
            )

        def connection_made(self, transport):
            """Set the transport."""
            self.transport = transport
            self._connected = True
            _LOGGER.info(
                "Miio push server started with address=%s server_id=%s",
                self.parent._address,
                self.parent.server_id,
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
            _LOGGER.debug("%s:%s<=ACK(server_id=%s)", host, port, self.parent.server_id)

        def send_msg_OK(self, host, port, msg_id, token):
            # This result means OK, but some methods return ['ok'] instead of 0
            # might be necessary to use different results for different methods
            result = {"result": 0, "id": msg_id}
            header = {
                "length": 0,
                "unknown": 0,
                "device_id": self.parent.server_id,
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

                if host not in self.parent._registered_devices:
                    _LOGGER.warning(
                        "Datagram received from unknown device (%s:%s)",
                        host,
                        port,
                    )
                    return

                token = self.parent._registered_devices[host]["token"]
                callback = self.parent._registered_devices[host]["callback"]

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
