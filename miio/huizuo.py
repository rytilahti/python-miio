import click

from .click_common import command, format_output
from .device import Device
from .exceptions import DeviceException

"""
Basic implementation for HUAYI HUIZUO PISCES For Bedroom (huayi.light.pis123) lamp

This lamp is white color only and supports dimming and control of the temperature from 3000K to 6400K
Specs: https://miot-spec.org/miot-spec-v2/instance?type=urn:miot-spec-v2:device:light:0000A001:huayi-pis123:1

"""

MODEL_HUIZUO_PIS123 = "huayi.light.pis123"

MODELS_SUPPORTED = [MODEL_HUIZUO_PIS123]


class HuizuoException(DeviceException):
    pass


class HuizuoStatus:
    def __init__(self, data):
        # power = '{"siid":2,"piid":1}' values = true,false
        # brightless = '{"siid":2,"piid":2}' values = 1-100
        # color-temperature = '{"siid":2,"piid":3}' values = 3000-6400
        self.data = data

    @property
    def is_on(self) -> bool:
        """Return whether the bulb is on or off."""
        return self.data["power"]

    @property
    def brightness(self) -> int:
        """Return current brightness."""
        return self.data["brightness"]

    @property
    def color_temp(self) -> int:
        """Return current color temperature."""
        return self.data["temperature"]

    def __repr__(self):
        s = "<Huizuo on=%s brightness=%s color_temp=%s>" % (
            self.is_on,
            self.brightness,
            self.color_temp,
        )
        return s


class Huizuo(Device):
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
        super().__init__(ip, token, start_id, debug, lazy_discover)

        if model in MODELS_SUPPORTED:
            self.model = model
        else:
            self.model = MODEL_HUIZUO_PIS123
            _LOGGER.error(
                "Device model %s unsupported. Falling back to %s.", model, self.model
            )

    @command(
        default_output=format_output(
            "\n",
            "Power: {result.is_on}\n"
            "Brightness: {result.brightness}\n"
            "Temperature: {result.color_temp}\n"
            "\n",
        )
    )
    def status(self) -> HuizuoStatus:
        """Retrieve properties."""
        properties = [
            {"siid": 2, "piid": 1},
            {"siid": 2, "piid": 2},
            {"siid": 2, "piid": 3},
        ]
        properties_name = ["power", "brightness", "temperature"]

        values = self.get_properties(properties)
        values_info = []
        for value in values:
            values_info.append(value["value"])
        return HuizuoStatus(dict(zip(properties_name, values_info)))

    @command(
        default_output=format_output("Powering on"),
    )
    def on(self):
        """Power on."""
        return self.raw_command("set_prop", [{"siid": 2, "piid": 1, "value": True}])

    @command(
        default_output=format_output("Powering off"),
    )
    def off(self):
        """Power off."""
        return self.raw_command("set_prop", [{"siid": 2, "piid": 1, "value": False}])

    @command(
        click.argument("level", type=int),
        default_output=format_output("Setting brightness to {level}"),
    )
    def set_brightness(self, level):
        """Set brightness."""
        if level < 0 or level > 100:
            raise HuizuoException("Invalid brightness: %s" % level)
        click.argument("level", type=int),
        return self.raw_command("set_prop", [{"siid": 2, "piid": 2, "value": level}])

    @command(
        click.argument("level", type=int),
        default_output=format_output("Setting color temperature to {level}"),
    )
    def set_color_temp(self, level):
        """Set color temp in kelvin."""
        if level > 6400 or level < 3000:
            raise HuizuoException("Invalid color temperature: %s" % level)
        click.argument("color_temp")
        return self.raw_command("set_prop", [{"siid": 2, "piid": 3, "value": level}])

    def __str__(self):
        return "<Huizuo at %s: %s>" % (self.ip, self.token)
