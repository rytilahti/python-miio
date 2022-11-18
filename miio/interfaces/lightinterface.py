"""`LightInterface` is an interface (abstract class) for light devices."""
from abc import abstractmethod
from typing import NamedTuple, Optional, Tuple


class ColorTemperatureRange(NamedTuple):
    """Color temperature range."""

    min: int
    max: int


class LightInterface:
    """Light interface."""

    @abstractmethod
    def set_power(self, on: bool, **kwargs):
        """Turn device on or off."""

    @abstractmethod
    def set_brightness(self, level: int, **kwargs):
        """Set the light brightness [0,100]."""

    @property
    def color_temperature_range(self) -> Optional[ColorTemperatureRange]:
        """Return the color temperature range, if supported."""
        return None

    def set_color_temperature(self, level: int, **kwargs):
        """Set color temperature in kelvin."""
        raise NotImplementedError(
            "Called set_color_temperature on device that does not support it"
        )

    def set_rgb(self, rgb: Tuple[int, int, int], **kwargs):
        """Set color in RGB."""
        raise NotImplementedError("Called set_rgb on device that does not support it")
