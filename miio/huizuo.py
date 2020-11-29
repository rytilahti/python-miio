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

MODELS_SUPPORTED = [
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
    MODEL_HUIZUO_ZW131
    ]


_MAPPING = {
    "power": {"siid": 2, "piid": 1}, # Boolean: True, False
    "brightness": {"siid": 2, "piid": 2}, # Percentage: 1-100
    "color_temp": {"siid": 2, "piid": 3}, # Kelvin: 3000-6400 (but for MODEL_HUIZUO_FANWY2: 3000-5700!)
}

_MAPPING_FAN_WY2 = { # for MODEL_HUIZUO_FANWY2
    "fan_power": {"siid": 3, "piid": 1}, # Boolean: True, False
    "fan_level": {"siid": 3, "piid": 2}, # Percentage: 1-100
    "fan_mode": {"siid": 3, "piid": 3}, # Enum: 0 - Basic, 1 - Natural wind
}

_MAPPING_FAN_WY = { # for MODEL_HUIZUO_FANWY
    "fan_power": {"siid": 3, "piid": 1}, # Boolean: True, False
    "fan_level": {"siid": 3, "piid": 2}, # Percentage: 1-100
    "fan_motor_reverse": {"siid": 3, "piid": 3}, # Boolean: True, False
    "fan_mode": {"siid": 3, "piid": 4}, # Enum: 0 - Basic, 1 - Natural wind
}

_MAPPING_HEATER = {
    "heater_power": {"siid": 3, "piid": 1}, # Boolean: True, False
    "heater_fault_code": {"siid": 3, "piid": 1}, # Fault code: 0 means "No fault"
    "heat_level": {"siid": 3, "piid": 1}, # Enum: 1-3
}

_MAPPING_SCENE = { # Only for write, send "0" to activate
    "on_off": {"siid": 3, "piid": 1}, 
    "brightness_add": {"siid": 3, "piid": 2},
    "brightness_dec": {"siid": 3, "piid": 3},
    "brightness_switch": {"siid": 3, "piid": 4},
    "colortemp_add": {"siid": 3, "piid": 5},
    "colortemp_dec": {"siid": 3, "piid": 6},
    "colortemp_switch": {"siid": 3, "piid": 7},
    "on_or_brightness": {"siid": 3, "piid": 8},
    "on_or_colortemp":  {"siid": 3, "piid": 9},
}

_AVAILABLE_MAPPING = {
    MODEL_HUIZUO_PIS123: _MAPPING,
    MODEL_HUIZUO_ARI013: _MAPPING,
    MODEL_HUIZUO_ARIES: _MAPPING,
    MODEL_HUIZUO_PEG091: _MAPPING,
    MODEL_HUIZUO_PEG093: _MAPPING,
    MODEL_HUIZUO_PISCES: _MAPPING,
    MODEL_HUIZUO_TAU023: _MAPPING,
    MODEL_HUIZUO_TAURUS: _MAPPING,
    MODEL_HUIZUO_VIR063: _MAPPING,
    MODEL_HUIZUO_VIRGO: _MAPPING,
    MODEL_HUIZUO_WY: _MAPPING,
    MODEL_HUIZUO_ZW131: _MAPPING,
    MODEL_HUIZUO_FANWY: _MAPPING + _MAPPING_FAN_WY,
    MODEL_HUIZUO_FANWY2: _MAPPING + _MAPPING_FAN_WY2,
    MODEL_HUIZUO_WY200: _MAPPING + _MAPPING_SCENE,
    MODEL_HUIZUO_WY201: _MAPPING + _MAPPING_SCENE,
    MODEL_HUIZUO_WY202: _MAPPING + _MAPPING_SCENE,
    MODEL_HUIZUO_WY203: _MAPPING + _MAPPING_SCENE,
    MODEL_HUIZUO_WYHEAT: _MAPPING + _MAPPING_SCENE
}


class HuizuoException(DeviceException):
    pass


class HuizuoStatus:
    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Response of a Huizuo Pisces For Bedroom (huayi.light.pis123)
         {'id': 1, 'result': [
             {'did': '', 'siid': 2, 'piid': 1, 'code': 0, 'value': False},
             {'did': '', 'siid': 2, 'piid': 2, 'code': 0, 'value': 94},
             {'did': '', 'siid': 2, 'piid': 3, 'code': 0, 'value': 6400}
             ]
        }

        Explanation (line-by-line):
            power = '{"siid":2,"piid":1}' values = true,false
            brightless(%) = '{"siid":2,"piid":2}' values = 1-100
            color temperature(Kelvin) = '{"siid":2,"piid":3}' values = 3000-6400
        """

        self.data = data

    @property
    def is_on(self) -> bool:
        """Return True if device is on."""
        return self.data["power"]

    @property
    def brightness(self) -> int:
        """Return current brightness."""
        return self.data["brightness"]

    @property
    def color_temp(self) -> int:
        """Return current color temperature."""
        return self.data["color_temp"]

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
    def is_heater_on(self):
        """Return True if Heater is on."""
        if "heater_power" in self.data:
            return self.data["heater_power"]
        return None

    @property
    def heater_fault_code(self):
        """Return Heater's fault code. 0 - No Fault"""
        if "heater_fault_code" in self.data:
            return self.data["heater_fault_code"]
        return None
    
    @property
    def heat_level(self):
        """Return Heater's heat level"""
        if "heat_level" in self.data:
            return self.data["heat_level"]
        return None

    def __repr__(self):
        parameters = []
        if self.is_on is not None: parameters.append("on="+self.is_on) 
        if self.brightness is not None: parameters.append("brightness="+self.brightness)
        if self.color_temp is not None: parameters.append("color_temp="+self.color_temp)
        if self.is_fan_on is not None: parameters.append("fan_on="+self.is_fan_on)
        if self.fan_speed_level is not None: parameters.append("fan_level="+self.fan_speed_level)
        if self.fan_mode is not None: parameters.append("fan_mode="+self.fan_mode)
        if self.is_fan_reverse is not None: parameters.append("fan_motor_reverse="+self.is_fan_reverse)
        if self.is_heater_on is not None: parameters.append("heater_on="+self.is_heater_on)
        if self.heat_level is not None: parameters.append("heat_level="+self.heat_level)
        if self.heater_fault_code is not None: parameters.append("heater_fault_code="+self.heater_fault_code)
    
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
        super().__init__(_MAPPING, ip, token, start_id, debug, lazy_discover)

        if model in MODELS_SUPPORTED:
            self.model = model
        else:
            self.model = MODEL_HUIZUO_PIS123
            _LOGGER.error(
                "Device model %s unsupported. Falling back to %s.", model, self.model
            )

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
            "Power: {result.is_on}\n"
            "Brightness: {result.brightness}\n"
            "Color Temperature: {result.color_temp}\n"
            "\n",
        )
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
        if color_temp < 3000 or color_temp > 6400:
            raise HuizuoException("Invalid color temperature: %s" % color_temp)

        return self.set_property("color_temp", color_temp)
