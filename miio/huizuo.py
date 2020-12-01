"""
Basic implementation for HUAYI HUIZUO LAMPS (huayi.light.*)

These lamps have a white color only and support dimming and control of the temperature from 3000K to 6400K

"""

import logging
from typing import Any, Dict

import click

from .click_common import command, format_output
from .exceptions import DeviceException
from .miot_device import MiotDevice

_LOGGER = logging.getLogger(__name__)

# Lights with the basic support
MODEL_HUIZUO_PIS123 = "huayi.light.pis123"
MODEL_HUIZUO_ARI013 = "huayi.light.ari013"
MODEL_HUIZUO_ARIES = "huayi.light.aries"
MODEL_HUIZUO_PEG091 = "huayi.light.peg091"
MODEL_HUIZUO_PEG093 = "huayi.light.peg093"
MODEL_HUIZUO_PISCES = "huayi.light.pisces"
MODEL_HUIZUO_TAU023 = "huayi.light.tau023"
MODEL_HUIZUO_TAURUS = "huayi.light.taurus"
MODEL_HUIZUO_VIR063 = "huayi.light.vir063"
MODEL_HUIZUO_VIRGO = "huayi.light.virgo"
MODEL_HUIZUO_WY = "huayi.light.wy"
MODEL_HUIZUO_ZW131 = "huayi.light.zw131"

# Lights: basic + fan
MODEL_HUIZUO_FANWY = "huayi.light.fanwy"
MODEL_HUIZUO_FANWY2 = "huayi.light.fanwy2"

# Lights: basic + scene
MODEL_HUIZUO_WY200 = "huayi.light.wy200"
MODEL_HUIZUO_WY201 = "huayi.light.wy201"
MODEL_HUIZUO_WY202 = "huayi.light.wy202"
MODEL_HUIZUO_WY203 = "huayi.light.wy203"

# Lights: basic + heater
MODEL_HUIZUO_WYHEAT = "huayi.light.wyheat"

BASIC_MODELS = [
    MODEL_HUIZUO_PIS123,
    MODEL_HUIZUO_ARI013,
    MODEL_HUIZUO_ARIES,
    MODEL_HUIZUO_PEG091,
    MODEL_HUIZUO_PEG093,
    MODEL_HUIZUO_PISCES,
    MODEL_HUIZUO_TAU023,
    MODEL_HUIZUO_TAURUS,
    MODEL_HUIZUO_VIR063,
    MODEL_HUIZUO_VIRGO,
    MODEL_HUIZUO_WY,
    MODEL_HUIZUO_ZW131,
]

MODELS_WITH_FAN_WY = [MODEL_HUIZUO_FANWY]
MODELS_WITH_FAN_WY2 = [MODEL_HUIZUO_FANWY2]

MODELS_WITH_SCENES = [
    MODEL_HUIZUO_WY200,
    MODEL_HUIZUO_WY201,
    MODEL_HUIZUO_WY202,
    MODEL_HUIZUO_WY203,
]

MODELS_WITH_HEATER = [MODEL_HUIZUO_WYHEAT]

MODELS_SUPPORTED = BASIC_MODELS

# Define a basic mapping for properties, which exists for all lights
_MAPPING = {
    "power": {"siid": 2, "piid": 1},  # Boolean: True, False
    "brightness": {"siid": 2, "piid": 2},  # Percentage: 1-100
    "color_temp": {
        "siid": 2,
        "piid": 3,
    },  # Kelvin: 3000-6400 (but for MODEL_HUIZUO_FANWY2: 3000-5700!)
}

_ADDITIONAL_MAPPING_FAN_WY2 = {  # for MODEL_HUIZUO_FANWY2
    "fan_power": {"siid": 3, "piid": 1},  # Boolean: True, False
    "fan_level": {"siid": 3, "piid": 2},  # Percentage: 1-100
    "fan_mode": {"siid": 3, "piid": 3},  # Enum: 0 - Basic, 1 - Natural wind
}

_ADDITIONAL_MAPPING_FAN_WY = {  # for MODEL_HUIZUO_FANWY
    "fan_power": {"siid": 3, "piid": 1},  # Boolean: True, False
    "fan_level": {"siid": 3, "piid": 2},  # Percentage: 1-100
    "fan_motor_reverse": {"siid": 3, "piid": 3},  # Boolean: True, False
    "fan_mode": {"siid": 3, "piid": 4},  # Enum: 0 - Basic, 1 - Natural wind
}

_ADDITIONAL_MAPPING_HEATER = {
    "heater_power": {"siid": 3, "piid": 1},  # Boolean: True, False
    "heater_fault_code": {"siid": 3, "piid": 1},  # Fault code: 0 means "No fault"
    "heat_level": {"siid": 3, "piid": 1},  # Enum: 1-3
}

_ADDITIONAL_MAPPING_SCENE = {  # Only for write, send "0" to activate
    "on_off": {"siid": 3, "piid": 1},
    "brightness_add": {"siid": 3, "piid": 2},
    "brightness_dec": {"siid": 3, "piid": 3},
    "brightness_switch": {"siid": 3, "piid": 4},
    "colortemp_add": {"siid": 3, "piid": 5},
    "colortemp_dec": {"siid": 3, "piid": 6},
    "colortemp_switch": {"siid": 3, "piid": 7},
    "on_or_brightness": {"siid": 3, "piid": 8},
    "on_or_colortemp": {"siid": 3, "piid": 9},
}



class HuizuoException(DeviceException):
    pass


class HuizuoStatus:
    def __init__(self, data: Dict[str, Any]) -> None:
        self.data = data

    @property
    def is_on(self) -> bool:
        """Return True if device is on."""
        if "power" in self.data:
            return self.data["power"]
        return None

    @property
    def brightness(self) -> int:
        """Return current brightness."""
        if "brightness" in self.data:
            return self.data["brightness"]
        return None

    @property
    def color_temp(self) -> int:
        """Return current color temperature."""
        if "color_temp" in self.data:
            return self.data["color_temp"]
        return None

    @property
    def is_fan_on(self) -> bool:
        """Return True if Fan is on."""
        if "fan_power" in self.data:
            return self.data["fan_power"]
        return None

    @property
    def fan_speed_level(self) -> int:
        """Return current Fan speed level."""
        if "fan_level" in self.data:
            return self.data["fan_level"]
        return None

    @property
    def is_fan_reverse(self) -> bool:
        """Return True if Fan reverse is on."""
        if "fan_motor_reverse" in self.data:
            return self.data["fan_motor_reverse"]
        return None

    @property
    def fan_mode(self) -> int:
        """Return 0 if 'Basic' and 1 if 'Natural wind'"""
        if "fan_mode" in self.data:
            return self.data["fan_mode"]
        return None

    @property
    def is_heater_on(self) -> bool:
        """Return True if Heater is on."""
        if "heater_power" in self.data:
            return self.data["heater_power"]
        return None

    @property
    def heater_fault_code(self) -> int:
        """Return Heater's fault code. 0 - No Fault"""
        if "heater_fault_code" in self.data:
            return self.data["heater_fault_code"]
        return None

    @property
    def heat_level(self) -> int:
        """Return Heater's heat level"""
        if "heat_level" in self.data:
            return self.data["heat_level"]
        return None

    def __repr__(self):
        parameters = []
        if self.is_on is not None:
            parameters.append("on=" + self.is_on)
        if self.brightness is not None:
            parameters.append("brightness=" + self.brightness)
        if self.color_temp is not None:
            parameters.append("color_temp=" + self.color_temp)
        if self.is_fan_on is not None:
            parameters.append("fan_on=" + self.is_fan_on)
        if self.fan_speed_level is not None:
            parameters.append("fan_level=" + self.fan_speed_level)
        if self.fan_mode is not None:
            parameters.append("fan_mode=" + self.fan_mode)
        if self.is_fan_reverse is not None:
            parameters.append("fan_motor_reverse=" + self.is_fan_reverse)
        if self.is_heater_on is not None:
            parameters.append("heater_on=" + self.is_heater_on)
        if self.heat_level is not None:
            parameters.append("heat_level=" + self.heat_level)
        if self.heater_fault_code is not None:
            parameters.append("heater_fault_code=" + self.heater_fault_code)

        s = "<Huizuo " + " ".join(parameters) + ">"
        return s


class Huizuo(MiotDevice):
    """A support for Huizuo PIS123."""

    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
        model: str = MODEL_HUIZUO_PIS123,
    ) -> None:

        if model in MODELS_WITH_FAN_WY:
            _MAPPING.update(_ADDITIONAL_MAPPING_FAN_WY)
        if model in MODELS_WITH_FAN_WY2:
            _MAPPING.update(_ADDITIONAL_MAPPING_FAN_WY2)
        if model in MODELS_WITH_SCENES:
            _MAPPING.update(_ADDITIONAL_MAPPING_SCENE)
        if model in MODELS_WITH_HEATER:
            _MAPPING.update(_ADDITIONAL_MAPPING_HEATER)

        super().__init__(_MAPPING, ip, token, start_id, debug, lazy_discover)

        if model in MODELS_SUPPORTED:
            self.model = model
        else:
            self.model = MODEL_HUIZUO_PIS123
            _LOGGER.error("Device model %s unsupported. Falling back to %s.", model, self.model)

    @command(
        default_output=format_output("Powering on"),
    )
    def on(self):
        """Power on."""
        return self.set_property("power", True)

    @command(
        default_output=format_output("Powering off"),
    )
    def off(self):
        """Power off."""
        return self.set_property("power", False)

    @command(
        default_output=format_output(
            "\n",
            "------------ Basic parameters for lamp -----------\n" 
            "Power: {result.is_on}\n"
            "Brightness: {result.brightness}\n"
            "Color Temperature: {result.color_temp}\n"
            "\n"
            "--------- Parameters for models with fan ---------\n"
            "Fan power:  {result.is_fan_on}\n"
            "Fan level: {result.fan_speed_level}\n"
            "Fan mode: {result.fan_mode}\n"
            "Fan reverse: {result.is_fan_reverse}\n"
            "\n"
            "------- Parameters for models with heater --------\n"
            "Heater power: {result.is_heater_on}\n"
            "Heat level: {result.heat_level}\n"
            "Heat fault code (0 means 'OK'): {result.heater_fault_code}\n",
        ),
    )
    def status(self) -> HuizuoStatus:
        """Retrieve properties."""

        return HuizuoStatus(
            {
                prop["did"]: prop["value"] if prop["code"] == 0 else None
                for prop in self.get_properties_for_mapping()
            }
        )

    @command(
        click.argument("level", type=int),
        default_output=format_output("Setting brightness to {level}"),
    )
    def set_brightness(self, level):
        """Set brightness."""
        if level < 0 or level > 100:
            raise HuizuoException("Invalid brightness: %s" % level)

        return self.set_property("brightness", level)

    @command(
        click.argument("color_temp", type=int),
        default_output=format_output("Setting color temperature to {color_temp}"),
    )
    def set_color_temp(self, color_temp):
        """Set color temp in kelvin."""

        # I don't know why only one lamp has smaller color temperature (based on specs),
        # but let's process it correctly
        if self.model == MODELS_WITH_FAN_WY2:
            max_color_temp = 5700
        else:
            max_color_temp = 6400

        if color_temp < 3000 or color_temp > max_color_temp:
            raise HuizuoException("Invalid color temperature: %s" % color_temp)

        return self.set_property("color_temp", color_temp)
