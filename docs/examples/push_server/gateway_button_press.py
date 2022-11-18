import asyncio
import logging

from miio import Gateway, PushServer
from miio.push_server import EventInfo

_LOGGER = logging.getLogger(__name__)
logging.basicConfig(level="INFO")

gateway_ip = "192.168.1.IP"
token = "TokenTokenToken"  # nosec
button_sid = "lumi.123456789abcdef"


async def asyncio_demo(loop):
    def subdevice_callback(source_device, action, params):
        _LOGGER.info(
            "callback '%s' from '%s', params: '%s'", action, source_device, params
        )

    push_server = PushServer(gateway_ip)
    gateway = Gateway(gateway_ip, token)

    await push_server.start()

    push_server.register_miio_device(gateway, subdevice_callback)

    await loop.run_in_executor(None, gateway.discover_devices)

    button = gateway.devices[button_sid]

    event_info = EventInfo(
        action="click_ch0",
        extra="[1,13,1,85,[0,1],0,0]",
        source_sid=button.sid,
        source_model=button.zigbee_model,
    )

    await push_server.subscribe_event(gateway, event_info)

    _LOGGER.info("Listening")

    await asyncio.sleep(30)

    await push_server.stop()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio_demo(loop))
