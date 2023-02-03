import asyncio
import logging
import socket
from json import dumps
from random import randint
from typing import Callable, Dict, Optional, Union

from ..device import Device
from ..protocol import Utils
from .eventinfo import EventInfo
from .serverprotocol import ServerProtocol

_LOGGER = logging.getLogger(__name__)

SERVER_PORT = 54321
FAKE_DEVICE_ID = "120009025"
FAKE_DEVICE_MODEL = "chuangmi.plug.v3"

PushServerCallback = Callable[[str, str, str], None]
MethodDict = Dict[str, Union[Dict, Callable]]


def calculated_token_enc(token):
    token_bytes = bytes.fromhex(token)
    encrypted_token = Utils.encrypt(token_bytes, token_bytes)
    encrypted_token_hex = encrypted_token.hex()
    return encrypted_token_hex[0:32]


class PushServer:
    """Async UDP push server acting as a fake miio device to handle event notifications
    from other devices.

    Assuming you already have a miio_device class initialized::

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
        await push_server.subscribe_event(miio_device, event_info)
        # Now you will see the callback function beeing called whenever the event occurs
        await asyncio.sleep(30)
        # When done stop the push_server, this will send messages to all subscribed miio_devices to unsubscribe all events
        await push_server.stop()
    """

    def __init__(self, *, device_ip=None, device_id=None):
        """Initialize the class."""
        self._device_ip = device_ip

        self._address = "0.0.0.0"  # nosec
        self._server_ip = None

        self._device_id = device_id if device_id is not None else int(FAKE_DEVICE_ID)
        self._server_model = FAKE_DEVICE_MODEL

        self._loop = None
        self._listen_couroutine = None
        self._registered_devices = {}

        self._methods: MethodDict = {}

        self._event_id = 1000000

    async def start(self):
        """Start Miio push server."""
        if self._listen_couroutine is not None:
            _LOGGER.error("Miio push server already started, not starting another one.")
            return

        self._loop = asyncio.get_event_loop()

        transport, self._listen_couroutine = await self._create_udp_server()

        return transport, self._listen_couroutine

    async def stop(self):
        """Stop Miio push server."""
        if self._listen_couroutine is None:
            return

        for ip in list(self._registered_devices):
            await self.unregister_miio_device(self._registered_devices[ip]["device"])

        self._listen_couroutine.close()
        self._listen_couroutine = None
        self._loop = None

    def add_method(self, name: str, response: Union[Dict, Callable]):
        """Add a method to server.

        The response can be either a callable or a dictionary to send back as response.
        """
        self._methods[name] = response

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

    async def unregister_miio_device(self, device: Device):
        """Unregister a miio device from this push server."""
        device_info = self._registered_devices.get(device.ip)
        if device_info is None:
            _LOGGER.debug("Device with ip %s not registered, bailing out", device.ip)
            return

        for event_id in device_info["event_ids"]:
            await self.unsubscribe_event(device, event_id)
        self._registered_devices.pop(device.ip)
        _LOGGER.debug("push server: unregistered miio device with ip %s", device.ip)

    async def subscribe_event(
        self, device: Device, event_info: EventInfo
    ) -> Optional[str]:
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

        # device.device_id and device.model may do IO if device info is not cached, so run in executor.
        event_payload = await self._loop.run_in_executor(
            None,
            self._construct_event,
            event_id,
            event_info,
            device,
        )

        response = await self._loop.run_in_executor(
            None,
            device.send,
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

    async def unsubscribe_event(self, device: Device, event_id: str):
        """Unsubscribe from a event by id."""
        result = await self._loop.run_in_executor(
            None, device.send, "miIO.xdel", [event_id]
        )
        if result == ["ok"]:
            event_ids = self._registered_devices[device.ip]["event_ids"]
            if event_id in event_ids:
                event_ids.remove(event_id)
        else:
            _LOGGER.error("Error removing event_id %s: %s", event_id, result)

        return result

    async def _get_server_ip(self):
        """Connect to the miio device to get server_ip using a one time use socket."""
        get_ip_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        get_ip_socket.bind((self._address, SERVER_PORT))
        get_ip_socket.setblocking(False)
        await self._loop.sock_connect(get_ip_socket, (self._device_ip, SERVER_PORT))
        server_ip = get_ip_socket.getsockname()[0]
        get_ip_socket.close()
        _LOGGER.debug("Miio push server device ip=%s", server_ip)
        return server_ip

    async def _create_udp_server(self):
        """Create the UDP socket and protocol."""
        if self._device_ip is not None:
            self._server_ip = await self._get_server_ip()

        # Create a fresh socket that will be used for the push server
        udp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        udp_socket.bind((self._address, SERVER_PORT))
        udp_socket.setblocking(False)

        return await self._loop.create_datagram_endpoint(
            lambda: ServerProtocol(self._loop, udp_socket, self),
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
            "did": str(self.device_id),
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
    def device_id(self):
        """Return the ID of the fake device beeing emulated."""
        return self._device_id

    @property
    def server_model(self):
        """Return the model of the fake device beeing emulated."""
        return self._server_model

    @property
    def methods(self) -> MethodDict:
        """Return a dict of implemented methods."""
        return self._methods
