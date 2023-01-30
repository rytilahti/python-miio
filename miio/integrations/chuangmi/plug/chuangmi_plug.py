import logging
from collections import defaultdict
from typing import Any, Dict, Optional

import click

from miio import Device, DeviceException, DeviceStatus
from miio.click_common import command, format_output
from miio.utils import deprecated

_LOGGER = logging.getLogger(__name__)

MODEL_CHUANGMI_PLUG_V3 = "chuangmi.plug.v3"
MODEL_CHUANGMI_PLUG_V1 = "chuangmi.plug.v1"
MODEL_CHUANGMI_PLUG_M1 = "chuangmi.plug.m1"
MODEL_CHUANGMI_PLUG_M3 = "chuangmi.plug.m3"
MODEL_CHUANGMI_PLUG_V2 = "chuangmi.plug.v2"
MODEL_CHUANGMI_PLUG_HMI205 = "chuangmi.plug.hmi205"
MODEL_CHUANGMI_PLUG_HMI206 = "chuangmi.plug.hmi206"
MODEL_CHUANGMI_PLUG_HMI208 = "chuangmi.plug.hmi208"

AVAILABLE_PROPERTIES = {
    MODEL_CHUANGMI_PLUG_V1: ["on", "usb_on", "temperature"],
    MODEL_CHUANGMI_PLUG_V3: ["on", "usb_on", "temperature", "wifi_led"],
    MODEL_CHUANGMI_PLUG_M1: ["power", "temperature"],
    MODEL_CHUANGMI_PLUG_M3: ["power", "temperature"],
    MODEL_CHUANGMI_PLUG_V2: ["power", "temperature"],
    MODEL_CHUANGMI_PLUG_HMI205: ["power", "temperature"],
    MODEL_CHUANGMI_PLUG_HMI206: ["power", "temperature"],
    MODEL_CHUANGMI_PLUG_HMI208: ["power", "usb_on", "temperature"],
}


class ChuangmiPlugStatus(DeviceStatus):
    """Container for status reports from the plug."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """Response of a Chuangmi Plug V1 (chuangmi.plug.v1)

        { 'power': True, 'usb_on': True, 'temperature': 32 }

        Response of a Chuangmi Plug V3 (chuangmi.plug.v3):
        { 'on': True, 'usb_on': True, 'temperature': 32, 'wifi_led': True }
        """
        self.data = data

    @property
    def power(self) -> bool:
        """Current power state."""
        if "on" in self.data:
            return self.data["on"] is True or self.data["on"] == "on"
        elif "power" in self.data:
            return self.data["power"] == "on"

        raise DeviceException("There was neither 'on' or 'power' in data")

    @property
    def is_on(self) -> bool:
        """True if device is on."""
        return self.power

    @property
    def temperature(self) -> int:
        return self.data["temperature"]

    @property
    def usb_power(self) -> Optional[bool]:
        """True if USB is on."""
        if "usb_on" in self.data and self.data["usb_on"] is not None:
            return self.data["usb_on"]
        return None

    @property
    def load_power(self) -> Optional[float]:
        """Current power load, if available."""
        if "load_power" in self.data and self.data["load_power"] is not None:
            return float(self.data["load_power"])
        return None

    @property  # type: ignore
    @deprecated("Use led()")
    def wifi_led(self) -> Optional[bool]:
        """True if the wifi led is turned on."""
        return self.led

    @property
    def led(self) -> Optional[bool]:
        """True if the wifi led is turned on."""
        if "wifi_led" in self.data and self.data["wifi_led"] is not None:
            return self.data["wifi_led"] == "on"
        return None


class ChuangmiPlug(Device):
    """Main class representing the Chuangmi Plug."""

    _supported_models = list(AVAILABLE_PROPERTIES.keys())

    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "USB Power: {result.usb_power}\n"
            "Temperature: {result.temperature} °C\n"
            "Load power: {result.load_power}\n"
            "WiFi LED: {result.wifi_led}\n",
        )
    )
    def status(self) -> ChuangmiPlugStatus:
        """Retrieve properties."""
        properties = AVAILABLE_PROPERTIES.get(
            self.model, AVAILABLE_PROPERTIES[MODEL_CHUANGMI_PLUG_M1]
        ).copy()
        values = self.get_properties(properties)

        if self.model == MODEL_CHUANGMI_PLUG_V3:
            load_power = self.send("get_power")  # Response: [300]
            if len(load_power) == 1:
                properties.append("load_power")
                values.append(load_power[0] * 0.01)

        return ChuangmiPlugStatus(defaultdict(lambda: None, zip(properties, values)))

    @command(default_output=format_output("Powering on"))
    def on(self):
        """Power on."""
        if self.model == MODEL_CHUANGMI_PLUG_V1:
            return self.send("set_on")

        return self.send("set_power", ["on"])

    @command(default_output=format_output("Powering off"))
    def off(self):
        """Power off."""
        if self.model == MODEL_CHUANGMI_PLUG_V1:
            return self.send("set_off")

        return self.send("set_power", ["off"])

    @command(default_output=format_output("Powering USB on"))
    def usb_on(self):
        """Power on."""
        return self.send("set_usb_on")

    @command(default_output=format_output("Powering USB off"))
    def usb_off(self):
        """Power off."""
        return self.send("set_usb_off")

    @deprecated("Use set_led instead of set_wifi_led")
    @command(
        click.argument("wifi_led", type=bool),
        default_output=format_output(
            lambda wifi_led: "Turning on WiFi LED"
            if wifi_led
            else "Turning off WiFi LED"
        ),
    )
    def set_wifi_led(self, wifi_led: bool):
        """Set the wifi led on/off."""
        self.set_led(wifi_led)

    @command(
        click.argument("wifi_led", type=bool),
        default_output=format_output(
            lambda wifi_led: "Turning on LED" if wifi_led else "Turning off LED"
        ),
    )
    def set_led(self, wifi_led: bool):
        """Set the led on/off."""
        if wifi_led:
            return self.send("set_wifi_led", ["on"])
        else:
            return self.send("set_wifi_led", ["off"])
