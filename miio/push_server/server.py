import asyncio
import logging
import socket
from json import dumps
from random import randint
from typing import Callable, Optional

from ..device import Device
from ..protocol import Utils
from .eventinfo import EventInfo
from .serverprotocol import ServerProtocol

_LOGGER = logging.getLogger(__name__)

SERVER_PORT = 54321
FAKE_DEVICE_ID = "120009025"
FAKE_DEVICE_MODEL = "chuangmi.plug.v3"

PushServerCallback = Callable[[str, str, str], None]


def calculated_token_enc(token):
    token_bytes = bytes.fromhex(token)
    encrypted_token = Utils.encrypt(token_bytes, token_bytes)
    encrypted_token_hex = encrypted_token.hex()
    return encrypted_token_hex[0:32]


class PushServer:
    """Async UDP push server acting as a fake miio device to handle event notifications
    from other devices.

    Assuming you already have a miio_device class initialized:

    # First create the push server
    push_server = PushServer(miio_device.ip)
    # Then start the server
    await push_server.start()
    # Register the miio device to the server and specify a callback function to receive events for this device
    # The callback function schould have the form of "def callback_func(source_device, action, params):"
    push_server.register_miio_device(miio_device, callback_func)
    # create a EventInfo object with the information about the event you which to subscribe to (information taken from packet captures of automations in the mi home app)
    event_info = EventInfo(
        action="alarm_triggering",
        extra="[1,19,1,111,[0,1],2,0]",
        trigger_token=miio_device.token,
    )
    # Send a message to the miio_device to subscribe for the event to receive messages on the push_server
    await loop.run_in_executor(None, push_server.subscribe_event, miio_device, event_info)
    # Now you will see the callback function beeing called whenever the event occurs
    await asyncio.sleep(30)
    # When done stop the push_server, this will send messages to all subscribed miio_devices to unsubscribe all events
    push_server.stop()
    """

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

    def register_miio_device(self, device: Device, callback: PushServerCallback):
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

    def subscribe_event(self, device: Device, event_info: EventInfo) -> Optional[str]:
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

    def unsubscribe_event(self, device: Device, event_id: str):
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
            lambda: ServerProtocol(loop, udp_socket, self),
            sock=udp_socket,
        )

    def _construct_event(  # nosec
        self,
        event_id: str,
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

        token_enc = calculated_token_enc(device.token)
        source_id = info.source_sid.replace(".", "_")
        command = f"{self.server_model}.{info.action}:{source_id}"
        key = f"event.{info.source_model}.{info.event}"
        message_id = 0
        magic_number = randint(
            1590161094, 1642025774
        )  # nosec, min/max taken from packet captures, unknown use

        if len(command) > 49:
            _LOGGER.error(
                "push server event command can be max 49 chars long,"
                " '%s' is %i chars, received callback command will be truncated",
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

        if info.trigger_value is not None:
            trigger_data["value"] = info.trigger_value

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
                    magic_number,
                    [
                        "0",
                        trigger_data,
                    ],
                    [target_data],
                ],
            ]
        ]

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
