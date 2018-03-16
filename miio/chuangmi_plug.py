import logging
from typing import Dict, Any, Optional
from collections import defaultdict
from .device import Device

_LOGGER = logging.getLogger(__name__)

MODEL_CHUANGMI_PLUG_V3 = 'chuangmi.plug.v3'
MODEL_CHUANGMI_PLUG_V1 = 'chuangmi.plug.v1'


class ChuangmiPlugStatus:
    """Container for status reports from the plug."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Response of a Chuangmi Plug V1 (chuangmi.plug.v1)
        { 'power': True, 'usb_on': True, 'temperature': 32 }

        Response of a Chuangmi Plug V3 (chuangmi.plug.v3):
        { 'on': True, 'usb_on': True, 'temperature': 32, 'wifi_led': True }
        """
        self.data = data

    @property
    def power(self) -> bool:
        """Current power state."""
        return self.data["on"]

    @property
    def is_on(self) -> bool:
        """True if device is on."""
        return self.power

    @property
    def usb_power(self) -> bool:
        """True if USB is on."""
        return self.data["usb_on"]

    @property
    def temperature(self) -> int:
        return self.data["temperature"]

    @property
    def load_power(self) -> Optional[int]:
        """Current power load, if available."""
        if self.data["load_power"] is not None:
            return self.data["load_power"]
        return None

    @property
    def wifi_led(self) -> Optional[bool]:
        """True if the wifi led is turned on."""
        if self.data["wifi_led"] is not None:
            return self.data["wifi_led"] == "on"
        return None

    def __repr__(self) -> str:
        s = "<ChuangmiPlugStatus " \
            "power=%s, " \
            "usb_power=%s, " \
            "temperature=%s" \
            "load_power=%s, " \
            "wifi_led=%s>" % \
            (self.power,
             self.usb_power,
             self.temperature,
             self.load_power,
             self.wifi_led)
        return s


class ChuangmiPlug(Device):
    """Main class representing the Chuangmi Plug V1 and V3."""

    def status(self) -> ChuangmiPlugStatus:
        """Retrieve properties."""
        properties = ['on', 'usb_on', 'temperature', 'wifi_led']
        values = self.send(
            "get_prop",
            properties
        )

        properties_count = len(properties)
        values_count = len(values)
        if properties_count != values_count:
            _LOGGER.debug(
                "Count (%s) of requested properties does not match the "
                "count (%s) of received values.",
                properties_count, values_count)

        if self.model == MODEL_CHUANGMI_PLUG_V3:
            load_power = self.send("get_power", [])  # Response: [300]
            if len(load_power) == 1:
                properties.append('load_power')
                values.append(load_power[0])

        return ChuangmiPlugStatus(
            defaultdict(lambda: None, zip(properties, values)))

    def on(self):
        """Power on."""
        return self.send("set_on", [])

    def off(self):
        """Power off."""
        return self.send("set_off", [])

    def usb_on(self):
        """Power on."""
        return self.send("set_usb_on", [])

    def usb_off(self):
        """Power off."""
        return self.send("set_usb_off", [])

    def set_wifi_led(self, led: bool):
        """Set the wifi led on/off."""
        if led:
            return self.send("set_wifi_led", ["on"])
        else:
            return self.send("set_wifi_led", ["off"])
