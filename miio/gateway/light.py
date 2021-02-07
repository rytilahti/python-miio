"""Xiaomi Gateway Light implementation."""

from typing import Tuple

import click

from ..click_common import command
from ..utils import brightness_and_color_to_int, int_to_brightness, int_to_rgb
from .gatewaydevice import GatewayDevice

color_map = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "white": (255, 255, 255),
    "yellow": (255, 255, 0),
    "orange": (255, 165, 0),
    "aqua": (0, 255, 255),
    "olive": (128, 128, 0),
    "purple": (128, 0, 128),
}


class Light(GatewayDevice):
    """Light controls for the gateway.

    The gateway LEDs can be controlled using 'rgb' or 'night_light' methods. The
    'night_light' methods control the same light as the 'rgb' methods, but has a
    separate memory for brightness and color. Changing the 'rgb' light does not affect
    the stored state of the 'night_light', while changing the 'night_light' does effect
    the state of the 'rgb' light.
    """

    @command()
    def rgb_status(self):
        """Get current status of the light. Always represents the current status of the
        light as opposed to 'night_light_status'.

        Example:
           {"is_on": false, "brightness": 0, "rgb": (0, 0, 0)}
        """
        # Returns {"is_on": false, "brightness": 0, "rgb": (0, 0, 0)} when light is off
        state_int = self._gateway.send("get_rgb").pop()
        brightness = int_to_brightness(state_int)
        rgb = int_to_rgb(state_int)
        is_on = brightness > 0

        return {"is_on": is_on, "brightness": brightness, "rgb": rgb}

    @command()
    def night_light_status(self):
        """Get status of the night light. This command only gives the correct status of
        the LEDs if the last command was a 'night_light' command and not a 'rgb' light
        command, otherwise it gives the stored values of the 'night_light'.

        Example:
           {"is_on": false, "brightness": 0, "rgb": (0, 0, 0)}
        """
        state_int = self._gateway.send("get_night_light_rgb").pop()
        brightness = int_to_brightness(state_int)
        rgb = int_to_rgb(state_int)
        is_on = brightness > 0

        return {"is_on": is_on, "brightness": brightness, "rgb": rgb}

    @command(
        click.argument("brightness", type=int),
        click.argument("rgb", type=(int, int, int)),
    )
    def set_rgb(self, brightness: int, rgb: Tuple[int, int, int]):
        """Set gateway light using brightness and rgb tuple."""
        brightness_and_color = brightness_and_color_to_int(brightness, rgb)

        return self._gateway.send("set_rgb", [brightness_and_color])

    @command(
        click.argument("brightness", type=int),
        click.argument("rgb", type=(int, int, int)),
    )
    def set_night_light(self, brightness: int, rgb: Tuple[int, int, int]):
        """Set gateway night light using brightness and rgb tuple."""
        brightness_and_color = brightness_and_color_to_int(brightness, rgb)

        return self._gateway.send("set_night_light_rgb", [brightness_and_color])

    @command(click.argument("brightness", type=int))
    def set_rgb_brightness(self, brightness: int):
        """Set gateway light brightness (0-100)."""
        if 100 < brightness < 0:
            raise Exception("Brightness must be between 0 and 100")
        current_color = self.rgb_status()["rgb"]

        return self.set_rgb(brightness, current_color)

    @command(click.argument("brightness", type=int))
    def set_night_light_brightness(self, brightness: int):
        """Set night light brightness (0-100)."""
        if 100 < brightness < 0:
            raise Exception("Brightness must be between 0 and 100")
        current_color = self.night_light_status()["rgb"]

        return self.set_night_light(brightness, current_color)

    @command(click.argument("color_name", type=str))
    def set_rgb_color(self, color_name: str):
        """Set gateway light color using color name ('color_map' variable in the source
        holds the valid values)."""
        if color_name not in color_map.keys():
            raise Exception(
                "Cannot find {color} in {colors}".format(
                    color=color_name, colors=color_map.keys()
                )
            )
        current_brightness = self.rgb_status()["brightness"]

        return self.set_rgb(current_brightness, color_map[color_name])

    @command(click.argument("color_name", type=str))
    def set_night_light_color(self, color_name: str):
        """Set night light color using color name ('color_map' variable in the source
        holds the valid values)."""
        if color_name not in color_map.keys():
            raise Exception(
                "Cannot find {color} in {colors}".format(
                    color=color_name, colors=color_map.keys()
                )
            )
        current_brightness = self.night_light_status()["brightness"]

        return self.set_night_light(current_brightness, color_map[color_name])

    @command(
        click.argument("color_name", type=str),
        click.argument("brightness", type=int),
    )
    def set_rgb_using_name(self, color_name: str, brightness: int):
        """Set gateway light color (using color name, 'color_map' variable in the source
        holds the valid values) and brightness (0-100)."""
        if 100 < brightness < 0:
            raise Exception("Brightness must be between 0 and 100")
        if color_name not in color_map.keys():
            raise Exception(
                "Cannot find {color} in {colors}".format(
                    color=color_name, colors=color_map.keys()
                )
            )

        return self.set_rgb(brightness, color_map[color_name])

    @command(
        click.argument("color_name", type=str),
        click.argument("brightness", type=int),
    )
    def set_night_light_using_name(self, color_name: str, brightness: int):
        """Set night light color (using color name, 'color_map' variable in the source
        holds the valid values) and brightness (0-100)."""
        if 100 < brightness < 0:
            raise Exception("Brightness must be between 0 and 100")
        if color_name not in color_map.keys():
            raise Exception(
                "Cannot find {color} in {colors}".format(
                    color=color_name, colors=color_map.keys()
                )
            )

        return self.set_night_light(brightness, color_map[color_name])
