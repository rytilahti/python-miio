import enum
import logging
from collections import defaultdict
from typing import Optional

from .click_common import command, format_output
from .device import Device, DeviceException

_LOGGER = logging.getLogger(__name__)

MODEL_AIRCONDITION_MA1 = 'zhimi.aircondition.ma1'

MODELS_SUPPORTED = [MODEL_AIRCONDITION_MA1]


class AirConditionException(DeviceException):
    pass


class OperationMode(enum.Enum):
    Arefaction = 'arefaction'
    Cool = 'cooling'
    Heat = 'heat'
    Wind = 'wind'


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
         'humidity': null,
         'speed_level': 5,
         'vertical_swing': 'on',
         'ptc': 'off',
         'ptc_rt': 'off',
         'silent': 'off',
         'vertical_end': 60,
         'vertical_rt': 19,
         'ele_quantity': null,
         'ex_humidity': null,
         'remote_mac': null,
         'htsensor_mac': null,
         'speed_level': 5,
         'vertical_swing': 'on',
         'ht_sensor': null,
         'comfort': 'off',
         'ot_run_temp': 7,
         'ep_temp': 27,
         'es_temp': 13,
         'he_temp': 39,
         'ot_humidity': null,
         'compressor_frq': 0,
         'motor_speed': 1000}

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
    def target_temperature(self) -> int:
        """Target temperature."""
        return self.data['st_temp_dec'] / 10.0

    @property
    def mode(self) -> Optional[OperationMode]:
        """Current operation mode."""
        try:
            return OperationMode(self.data['mode'])
        except TypeError:
            return None

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

        properties = ['mode', 'lcd_auto', 'lcd_level', 'volume', 'idle_timer', 'open_timer',
                      'power', 'temp_dec', 'st_temp_dec', 'speed_level', 'vertical_swing',
                      'ptc', 'ptc_rt', 'silent', 'vertical_end', 'vertical_rt', 'speed_level',
                      'vertical_swing', 'comfort', 'ot_run_temp', 'ep_temp', 'es_temp',
                      'he_temp', 'compressor_frq', 'motor_speed', 'humidity', 'ele_quantity',
                      'ex_humidity', 'remote_mac', 'htsensor_mac', 'ht_sensor', 'ot_humidity']

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
