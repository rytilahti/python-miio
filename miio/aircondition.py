import enum
import logging
from collections import defaultdict
from typing import Optional

import click

from .click_common import command, format_output, EnumType
from .device import Device, DeviceException

_LOGGER = logging.getLogger(__name__)

MODEL_AIRCONDITION_MA1 = 'zhimi.aircondition.ma1'
MODEL_AIRCONDITION_MA2 = 'zhimi.aircondition.ma2'
MODEL_AIRCONDITION_SA1 = 'zhimi.aircondition.sa1'

MODELS_SUPPORTED = [MODEL_AIRCONDITION_MA1, MODEL_AIRCONDITION_MA2, MODEL_AIRCONDITION_SA1]


class AirConditionException(DeviceException):
    pass


class OperationMode(enum.Enum):
    Arefaction = 'arefaction'
    Cool = 'cooling'
    Heat = 'heat'
    Wind = 'wind'
    Auto = 'automode'


class AirConditionStatus:
    """Container for status reports of the Xiaomi Air Condition."""

    def __init__(self, data):
        """
        Device model: zhimi.aircondition.ma1

        {'mode': 'cooling',
         'lcd_auto': 'off',
         'lcd_level': 1,
         'volume': 'off',
         'idle_timer': 0,
         'open_timer': 0,
         'power': 'on',
         'temp_dec': 244,
         'st_temp_dec': 320,
         'vertical_swing': 'on',
         'ptc': 'off',
         'ptc_rt': 'off',
         'silent': 'off',
         'vertical_end': 60,
         'vertical_rt': 19,
         'speed_level': 5,
         'comfort': 'off',
         'ot_run_temp': 7,
         'ep_temp': 27,
         'es_temp': 13,
         'he_temp': 39,
         'compressor_frq': 0,
         'motor_speed': 1000,
         'humidity': null,
         'ele_quantity': null,
         'ex_humidity': null,
         'remote_mac': null,
         'htsensor_mac': null,
         'ht_sensor': null,
         'ot_humidity': null}

        """
        self.data = data

    @property
    def power(self) -> str:
        """Current power state."""
        return self.data['power']

    @property
    def is_on(self) -> bool:
        """True if the device is turned on."""
        return self.power == 'on'

    @property
    def temperature(self) -> int:
        """Current temperature."""
        return self.data['temp_dec'] / 10.0

    @property
    def ot_run_temperature(self) -> int:
        """Outdoor operation temperature."""
        return self.data['ot_run_temp']

    @property
    def ep_temperature(self) -> int:
        """Outer ring temperature."""
        return self.data['ep_temp']

    @property
    def es_temperature(self) -> int:
        """Outer ring temperature."""
        return self.data['es_temp']

    @property
    def he_temperature(self) -> int:
        """Outlet temperature."""
        return self.data['he_temp']

    @property
    def target_temperature(self) -> int:
        """Target temperature."""
        return self.data['st_temp_dec'] / 10.0

    @property
    def humidity(self) -> Optional[int]:
        """Current indoor humidity."""
        return self.data["humidity"]

    def external_humidity(self) -> Optional[int]:
        """Current external humidity."""
        return self.data["ex_humidity"]

    @property
    def outdoor_humidity(self) -> Optional[int]:
        """Current outdoor humidity."""
        return self.data["ot_humidity"]

    @property
    def mode(self) -> Optional[OperationMode]:
        """Current operation mode."""
        try:
            return OperationMode(self.data['mode'])
        except TypeError:
            return None

    @property
    def lcd_auto(self) -> bool:
        """Automatic display brightness."""
        return self.data['lcd_auto'] == 'on'

    @property
    def display_brightness(self) -> int:
        """Display brightness."""
        return self.data['lcd_level']

    @property
    def audio(self) -> bool:
        """Audio output."""
        return self.data['volume'] == 'on'

    @property
    def swing(self) -> bool:
        """Vertical swing."""
        return self.data['vertical_swing'] == 'on'

    @property
    def electric_auxiliary_heat(self) -> bool:
        """Electric auxiliary heat."""
        return self.data['ptc'] == 'on'

    @property
    def ptc_rt(self) -> bool:
        """Ptc rt?"""
        return self.data['ptc'] == 'on'

    @property
    def silent(self) -> bool:
        """Silent mode."""
        return self.data['silent'] == 'on'

    @property
    def comfort(self) -> bool:
        """Comfort mode."""
        return self.data['comfort'] == 'on'

    @property
    def delay_off(self) -> int:
        """Delayed turn off."""
        return self.data['idle_timer']

    @property
    def open_timer(self) -> int:
        """Open timer?."""
        return self.data['open_timer']

    @property
    def speed(self) -> int:
        """Speed level."""
        return self.data['speed_level']

    @property
    def compressor_frequency(self) -> int:
        """Compressor frequency in Hz."""
        return self.data['compressor_frq']

    @property
    def motor_speed(self) -> int:
        """Motor speed."""
        return self.data['motor_speed']

    @property
    def swing_range(self) -> [int, int]:
        """Swing range."""
        return [self.data['vertical_rt'], self.data['vertical_end']]

    @property
    def power_consumption(self) -> float:
        """Power consumption in kWh."""
        return self.data['ele_quantity'] / 10.0

    @property
    def extra_features(self) -> Optional[int]:
        return self.data["app_extra"]

    def __repr__(self) -> str:
        s = "<AirConditionStatus " \
            "power=%s, " \
            "temperature=%s, " \
            "target_temperature=%s, " \
            "mode=%s>" % \
            (self.power,
             self.temperature,
             self.target_temperature,
             self.mode)
        return s

    def __json__(self):
        return self.data


class AirCondition(Device):
    """Main class representing Xiaomi Air Condition MA1."""

    def __init__(self, ip: str = None, token: str = None, start_id: int = 0,
                 debug: int = 0, lazy_discover: bool = True,
                 model: str = MODEL_AIRCONDITION_MA1) -> None:
        super().__init__(ip, token, start_id, debug, lazy_discover)

        if model in MODELS_SUPPORTED:
            self.model = model
        else:
            self.model = MODEL_AIRCONDITION_MA1
            _LOGGER.error("Device model %s unsupported. Falling back to %s.", model, self.model)

    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "Temperature: {result.temperature} °C\n"
            "Target temperature: {result.target_temperature} °C\n"
            "Mode: {result.mode}\n"
        )
    )
    def status(self) -> AirConditionStatus:
        """Retrieve properties."""

        properties = [
            'mode',
            'lcd_auto',
            'lcd_level',
            'volume',
            'idle_timer',
            'open_timer',
            'power',
            'temp_dec',
            'st_temp_dec',
            'vertical_swing',
            'ptc',
            'ptc_rt',
            'silent',
            'vertical_end',
            'vertical_rt',
            'speed_level',
            'comfort',
            'ot_run_temp',
            'ep_temp',
            'es_temp',
            'he_temp',
            'compressor_frq',
            'motor_speed',
            'app_extra',
            'humidity',
            'ele_quantity',
            'ex_humidity',
            'remote_mac',
            'htsensor_mac',
            'ht_sensor',
            'ot_humidity',
        ]

        # A single request is limited to 16 properties. Therefore the
        # properties are divided into multiple requests
        _props = properties.copy()
        values = []
        while _props:
            values.extend(self.send("get_prop", _props[:15]))
            _props[:] = _props[15:]

        properties_count = len(properties)
        values_count = len(values)
        if properties_count != values_count:
            _LOGGER.debug(
                "Count (%s) of requested properties does not match the "
                "count (%s) of received values.",
                properties_count, values_count)

        return AirConditionStatus(
            defaultdict(lambda: None, zip(properties, values)))

    @command(
        default_output=format_output("Powering the air condition on"),
    )
    def on(self):
        """Turn the air condition on."""
        return self.send("set_power", ["on"])

    @command(
        default_output=format_output("Powering the air condition off"),
    )
    def off(self):
        """Turn the air condition off."""
        return self.send("set_power", ["off"])

    @command(
        click.argument("temperature", type=float),
        default_output=format_output(
            "Setting target temperature to {temperature} degrees")
    )
    def set_temperature(self, temperature: float):
        """Set target temperature."""
        return self.send("set_temperature", [int(temperature * 10)])

    @command(
        click.argument("speed", type=int),
        default_output=format_output(
            "Setting speed to {speed}")
    )
    def set_speed(self, speed: int):
        """Set speed."""
        if speed < 0 or speed > 5:
            raise AirConditionException("Invalid speed level: %s", speed)

        return self.send("set_spd_level", [speed])

    @command(
        click.argument("start", type=int),
        click.argument("stop", type=int),
        default_output=format_output("Setting swing range from {start} degrees to {stop} degrees")
    )
    def set_swing_range(self, start: int=0, stop: int=60):
        """Set swing range."""
        if start < 0 or stop <= start or start > 60 or stop > 60:
            raise AirConditionException("Invalid swing range: %s %s", start, stop)

        return self.send("set_ver_range", [start, stop])

    @command(
        click.argument("swing", type=bool),
        default_output=format_output(
            lambda swing: "Turning on swing mode"
            if swing else "Turning off swing mode"
        )
    )
    def set_swing(self, swing: bool):
        """Set swing on/off."""
        if swing:
            return self.send("set_vertical", ["on"])
        else:
            return self.send("set_vertical", ["off"])

    @command(
        click.argument("direction", type=int),
        default_output=format_output(
            "Setting wind direction to {direction} degrees")
    )
    def set_wind_direction(self, direction: int):
        """Set wind direction."""
        if direction < 0 or direction > 60:
            raise AirConditionException("Invalid wind direction: %s", direction)

        return self.send("set_ver_pos", [direction])

    @command(
        click.argument("comfort", type=bool),
        default_output=format_output(
            lambda comfort: "Turning on comfort mode"
            if comfort else "Turning off comfort mode"
        )
    )
    def set_comfort(self, comfort: bool):
        """Set comfort on/off."""
        if comfort:
            return self.send("set_comfort", ["on"])
        else:
            return self.send("set_comfort", ["off"])

    @command(
        click.argument("silent", type=bool),
        default_output=format_output(
            lambda silent: "Turning on silent mode"
            if silent else "Turning off silent mode"
        )
    )
    def set_silent(self, silent: bool):
        """Set silent on/off."""
        if silent:
            return self.send("set_silent", ["on"])
        else:
            return self.send("set_silent", ["off"])

    @command(
        click.argument("power", type=bool),
        default_output=format_output(
            lambda power: "Turning on electric auxiliary heat"
            if power else "Turning off electric auxiliary heat"
        )
    )
    def set_electric_auxiliary_heat(self, power: bool):
        """Set electric auxiliary heat on/off."""
        if power:
            return self.send("set_ptc", ["on"])
        else:
            return self.send("set_ptc", ["off"])

    @command(
        click.argument("audio", type=bool),
        default_output=format_output(
            lambda audio: "Turning on audio"
            if audio else "Turning off audio"
        )
    )
    def set_audio(self, audio: bool):
        """Turn audio on/off."""
        if audio:
            return self.send("set_volume_sw", ["on"])
        else:
            return self.send("set_volume_sw", ["off"])

    @command(
        click.argument("brightness", type=int),
        default_output=format_output(
            "Setting display brightness to {brightness}")
    )
    def set_display_brightness(self, brightness: int):
        """Set display brightness."""
        if brightness < 0 or brightness > 5:
            raise AirConditionException("Invalid display brightness: %s", brightness)

        return self.send("set_lcd", [brightness])

    @command(
        click.argument("auto", type=bool),
        default_output=format_output(
            lambda auto: "Turning on auto display brightness"
            if auto else "Turning off auto display brightness"
        )
    )
    def set_auto_display_brightess(self, auto: bool):
        """Turn automatic display brightness on/off."""
        if auto:
            return self.send("set_lcd_auto", ["on"])
        else:
            return self.send("set_lcd_auto", ["off"])

    @command(
        click.argument("mode", type=EnumType(OperationMode, False)),
        default_output=format_output("Setting operation mode to '{mode.value}'")
    )
    def set_mode(self, mode: OperationMode):
        """Set operation mode."""
        return self.send("set_mode", [mode.value])

    @command(
        click.argument("seconds", type=int),
        default_output=format_output("Setting delayed turn off to {seconds} seconds")
    )
    def delay_off(self, seconds: int):
        """Set delay off seconds."""
        if seconds < 1:
            raise AirConditionException(
                "Invalid value for a delayed turn off: %s" % seconds)

        return self.send("set_idle_timer", [seconds])

    @command(
        click.argument("seconds", type=int),
        default_output=format_output("Setting open timer to {seconds} seconds")
    )
    def set_open_timer(self, seconds: int):
        """Set open timer."""
        if seconds < 1:
            raise AirConditionException(
                "Invalid open timer value: %s" % seconds)

        return self.send("set_open_timer", [seconds])

    @command(
        click.argument("value", type=int),
        default_output=format_output("Setting extra to {value}")
    )
    def set_extra_features(self, value: int):
        """Storage register to enable extra features at the app."""
        if value < 0:
            raise AirConditionException("Invalid app extra value: %s", value)

        return self.send("set_app_extra", [value])

    @command(
        click.argument("sensor", type=bool),
        default_output=format_output(
            lambda sensor: "Turning on humidity/temperature sensor"
            if sensor else "Turning off humidity/temperature sensor"
        )
    )
    def set_sensor(self, sensor: bool):
        """Turn automatic display brightness on/off."""
        if sensor:
            return self.send("set_ht_sensor", ["on"])
        else:
            return self.send("set_ht_sensor", ["off"])
