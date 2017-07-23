from .device import Device
from .containers import AirPurifierStatus


class AirPurifier(Device):
    """Main class representing the air purifier."""

    def status(self):
        """Retrieve properties."""

        # A few more properties:
        properties = ['power', 'aqi', 'humidity', 'temp_dec',
                      'mode', 'led', 'led_b', 'buzzer', 'child_lock',
                      'limit_hum', 'trans_level', 'bright',
                      'favorite_level', 'filter1_life', 'act_det',
                      'f1_hour_used', 'use_time', 'motor1_speed']

        values = self.send(
            "get_prop",
            properties
        )
        return AirPurifierStatus(dict(zip(properties, values)))

    def set_mode(self, mode: str):
        """Set mode."""

        # auto, silent, favorite, medium, high, strong, idle
        return self.send("set_mode", [mode])

    def set_favorite_level(self, level: int):
        """Set favorite level."""

        # Set the favorite level used when the mode is `favorite`,
        # should be  between 0 and 16.
        return self.send("favorite_level", [level])  # 0 ... 16

    def set_led_brightness(self, brightness: int):
        """Set led brightness."""

        # bright: 0, dim: 1, off: 2
        return self.send("set_led_b", [brightness])

    def set_led(self, led: bool):
        """Turn led on/off."""

        if led:
            return self.send("set_led", ['on'])
        else:
            return self.send("set_led", ['off'])

    def set_buzzer(self, buzzer: bool):
        """Set buzzer."""

        if buzzer:
            return self.send("set_mode", ["on"])
        else:
            return self.send("set_mode", ["off"])

    def set_humidity_limit(self, limit: int):
        """Set humidity limit."""

        # 40, 50, 60, 70 or 80
        return self.send("set_limit_hum", [limit])
