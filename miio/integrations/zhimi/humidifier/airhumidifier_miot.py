import enum
import logging
from typing import Any, Optional

import click

from miio import DeviceStatus, MiotDevice
from miio.click_common import EnumType, command, format_output
from miio.devicestatus import sensor, setting

_LOGGER = logging.getLogger(__name__)


SMARTMI_EVAPORATIVE_HUMIDIFIER_2 = "zhimi.humidifier.ca4"
SMARTMI_EVAPORATIVE_HUMIDIFIER_3 = "zhimi.humidifier.ca6"


_MAPPINGS_CA4 = {
    SMARTMI_EVAPORATIVE_HUMIDIFIER_2: {
        # Source http://miot-spec.org/miot-spec-v2/instance?type=urn:miot-spec-v2:device:humidifier:0000A00E:zhimi-ca4:2
        # Air Humidifier (siid=2)
        "power": {"siid": 2, "piid": 1},  # bool
        "fault": {"siid": 2, "piid": 2},  # [0, 15] step 1
        "mode": {"siid": 2, "piid": 5},  # 0 - Auto, 1 - lvl1, 2 - lvl2, 3 - lvl3
        "target_humidity": {"siid": 2, "piid": 6},  # [30, 80] step 1
        "water_level": {"siid": 2, "piid": 7},  # [0, 128] step 1
        "dry": {"siid": 2, "piid": 8},  # bool
        "use_time": {"siid": 2, "piid": 9},  # [0, 2147483600], step 1
        "button_pressed": {"siid": 2, "piid": 10},  # 0 - none, 1 - led, 2 - power
        "speed_level": {"siid": 2, "piid": 11},  # [200, 2000], step 10
        # Environment (siid=3)
        "temperature": {"siid": 3, "piid": 7},  # [-40, 125] step 0.1
        "fahrenheit": {"siid": 3, "piid": 8},  # [-40, 257] step 0.1
        "humidity": {"siid": 3, "piid": 9},  # [0, 100] step 1
        # Alarm (siid=4)
        "buzzer": {"siid": 4, "piid": 1},
        # Indicator Light (siid=5)
        "led_brightness": {"siid": 5, "piid": 2},  # 0 - Off, 1 - Dim, 2 - Brightest
        # Physical Control Locked (siid=6)
        "child_lock": {"siid": 6, "piid": 1},  # bool
        # Other (siid=7)
        "actual_speed": {"siid": 7, "piid": 1},  # [0, 2000] step 1
        "power_time": {"siid": 7, "piid": 3},  # [0, 4294967295] step 1
        "clean_mode": {"siid": 7, "piid": 5},  # bool
    }
}


_MAPPINGS_CA6 = {
    SMARTMI_EVAPORATIVE_HUMIDIFIER_3: {
        # Source https://miot-spec.org/miot-spec-v2/instance?type=urn:miot-spec-v2:device:humidifier:0000A00E:zhimi-ca6:1
        # Air Humidifier (siid=2)
        "power": {"siid": 2, "piid": 1},  # bool
        "fault": {"siid": 2, "piid": 2},  # [0, 15] step 1
        "mode": {
            "siid": 2,
            "piid": 5,
        },  # 0 - Fav, 1 - Auto, 2 - Sleep
        "target_humidity": {
            "siid": 2,
            "piid": 6,
        },  # [30, 60] step 1
        "water_level": {
            "siid": 2,
            "piid": 7,
        },  # 0 - empty/min,  1 - normal, 2 - full/max
        "dry": {"siid": 2, "piid": 8},  # Automatic Air Drying, bool
        "status": {"siid": 2, "piid": 9},  # 1 - Close, 2 - Work, 3 - Dry, 4 - Clean
        # Environment (siid=3)
        "temperature": {"siid": 3, "piid": 7},  # [-40, 125] step 0.1
        "humidity": {"siid": 3, "piid": 9},  # [0, 100] step 1
        # Alarm (siid=4)
        "buzzer": {"siid": 4, "piid": 1},
        # Indicator Light (siid=5)
        "led_brightness": {"siid": 5, "piid": 2},  # 0 - Off, 1 - Dim, 2 - Brightest
        # Physical Control Locked (siid=6)
        "child_lock": {"siid": 6, "piid": 1},  # bool
        # Other (siid=7)
        "actual_speed": {"siid": 7, "piid": 1},  # [0, 2000] step 1
        "country_code": {
            "siid": 7,
            "piid": 4,
        },  # 82 - KR, 44 - EU, 81 - JP, 86 - CN, 886 - TW
        "clean_mode": {"siid": 7, "piid": 5},  # bool
        "self_clean_percent": {"siid": 7, "piid": 6},  # minutes, [0, 30] step 1
        "pump_state": {"siid": 7, "piid": 7},  # bool
        "pump_cnt": {"siid": 7, "piid": 8},  # [0, 4000] step 1
    }
}


class OperationMode(enum.Enum):
    Auto = 0
    Low = 1
    Mid = 2
    High = 3


class OperationModeCA6(enum.Enum):
    Fav = 0
    Auto = 1
    Sleep = 2


class OperationStatusCA6(enum.Enum):
    Close = 1
    Work = 2
    Dry = 3
    Clean = 4


class LedBrightness(enum.Enum):
    Off = 0
    Dim = 1
    Bright = 2


class PressedButton(enum.Enum):
    No = 0
    Led = 1
    Power = 2


class AirHumidifierMiotCommonStatus(DeviceStatus):
    """Container for status reports from the air humidifier. Common features for CA4 and CA6 models."""

    def __init__(self, data: dict[str, Any]) -> None:
        self.data = data
        _LOGGER.debug(
            "Status Common: %s, __cli_output__ %s", repr(self), self.__cli_output__
        )

    # Air Humidifier

    @property
    def is_on(self) -> bool:
        """Return True if device is on."""
        return self.data["power"]

    @property
    def power(self) -> str:
        """Return power state."""
        return "on" if self.is_on else "off"

    @property
    def error(self) -> int:
        """Return error state."""
        return self.data["fault"]

    @property
    def target_humidity(self) -> int:
        """Return target humidity."""
        return self.data["target_humidity"]

    @property
    @setting(
        name="Dry Mode",
        icon="mdi:hair-dryer",
        setter_name="set_dry",
        device_class="switch",
        entity_category="config",
    )
    def dry(self) -> Optional[bool]:
        """Return True if dry mode is on."""
        if self.data["dry"] is not None:
            return self.data["dry"]
        return None

    @property
    @setting(
        name="Clean Mode",
        icon="mdi:shimmer",
        setter_name="set_clean_mode",
        device_class="switch",
        entity_category="config",
    )
    def clean_mode(self) -> bool:
        """Return True if clean mode is active."""
        return self.data["clean_mode"]

    # Environment

    @property
    @sensor("Humidity", unit="%", device_class="humidity")
    def humidity(self) -> int:
        """Return current humidity."""
        return self.data["humidity"]

    @property
    @sensor("Temperature", unit="°C", device_class="temperature")
    def temperature(self) -> Optional[float]:
        """Return current temperature, if available."""
        if self.data["temperature"] is not None:
            return round(self.data["temperature"], 1)
        return None

    # Alarm

    @property
    @setting(
        name="Buzzer",
        icon="mdi:volume-high",
        setter_name="set_buzzer",
        device_class="switch",
        entity_category="config",
    )
    def buzzer(self) -> Optional[bool]:
        """Return True if buzzer is on."""
        if self.data["buzzer"] is not None:
            return self.data["buzzer"]
        return None

    # Indicator Light

    @property
    @setting(
        name="Led Brightness",
        icon="mdi:brightness-6",
        setter_name="set_led_brightness",
        choices=LedBrightness,
        entity_category="config",
    )
    def led_brightness(self) -> Optional[LedBrightness]:
        """Return brightness of the LED."""

        if self.data["led_brightness"] is not None:
            try:
                return LedBrightness(self.data["led_brightness"])
            except ValueError as e:
                _LOGGER.exception("Cannot parse led_brightness: %s", e)
                return None

        return None

    # Physical Control Locked

    @property
    @setting(
        name="Child Lock",
        icon="mdi:lock",
        setter_name="set_child_lock",
        device_class="switch",
        entity_category="config",
    )
    def child_lock(self) -> bool:
        """Return True if child lock is on."""
        return self.data["child_lock"]

    # Other

    @property
    @sensor(
        "Actual Motor Speed",
        unit="rpm",
        device_class="measurement",
        icon="mdi:fast-forward",
        entity_category="diagnostic",
    )
    def actual_speed(self) -> int:
        """Return real speed of the motor."""
        return self.data["actual_speed"]


class AirHumidifierMiotStatus(AirHumidifierMiotCommonStatus):
    """Container for status reports from the air humidifier.

    Xiaomi Smartmi Evaporation Air Humidifier 2 (zhimi.humidifier.ca4) respone (MIoT format)::

        [
            {'did': 'power', 'siid': 2, 'piid': 1, 'code': 0, 'value': True},
            {'did': 'fault', 'siid': 2, 'piid': 2, 'code': 0, 'value': 0},
            {'did': 'mode', 'siid': 2, 'piid': 5, 'code': 0, 'value': 0},
            {'did': 'target_humidity', 'siid': 2, 'piid': 6, 'code': 0, 'value': 50},
            {'did': 'water_level', 'siid': 2, 'piid': 7, 'code': 0, 'value': 127},
            {'did': 'dry', 'siid': 2, 'piid': 8, 'code': 0, 'value': False},
            {'did': 'use_time', 'siid': 2, 'piid': 9, 'code': 0, 'value': 5140816},
            {'did': 'button_pressed', 'siid': 2, 'piid': 10, 'code': 0, 'value': 2},
            {'did': 'speed_level', 'siid': 2, 'piid': 11, 'code': 0, 'value': 790},
            {'did': 'temperature', 'siid': 3, 'piid': 7, 'code': 0, 'value': 22.7},
            {'did': 'fahrenheit', 'siid': 3, 'piid': 8, 'code': 0, 'value': 72.8},
            {'did': 'humidity', 'siid': 3, 'piid': 9, 'code': 0, 'value': 39},
            {'did': 'buzzer', 'siid': 4, 'piid': 1, 'code': 0, 'value': False},
            {'did': 'led_brightness', 'siid': 5, 'piid': 2, 'code': 0, 'value': 2},
            {'did': 'child_lock', 'siid': 6, 'piid': 1, 'code': 0, 'value': False},
            {'did': 'actual_speed', 'siid': 7, 'piid': 1, 'code': 0, 'value': 0},
            {'did': 'power_time', 'siid': 7, 'piid': 3, 'code': 0, 'value': 18520},
            {'did': 'clean_mode', 'siid': 7, 'piid': 5, 'code': 0, 'value': True}
        ]
    """

    def __init__(self, data: dict[str, Any]) -> None:
        self.data = data
        super().__init__(self.data)
        self.embed("common", AirHumidifierMiotCommonStatus(self.data))

    # Air Humidifier

    @property
    @setting(
        name="Operation Mode",
        setter_name="set_mode",
    )
    def mode(self) -> OperationMode:
        """Return current operation mode."""

        try:
            mode = OperationMode(self.data["mode"])
        except ValueError as e:
            _LOGGER.exception("Cannot parse mode: %s", e)
            return OperationMode.Auto

        return mode

    @property
    @sensor(
        "Water Level",
        unit="%",
        device_class="measurement",
        icon="mdi:water-check",
        entity_category="diagnostic",
    )
    def water_level(self) -> Optional[int]:
        """Return current water level in percent.

        If water tank is full, raw water_level value is 120. If water tank is
        overfilled, raw water_level value is 125.
        """
        water_level = self.data["water_level"]
        if water_level > 125:
            return None

        if water_level < 0:
            return 0

        return int(min(water_level / 1.2, 100))

    @property
    @sensor(
        "Water Tank Attached",
        device_class="connectivity",
        icon="mdi:car-coolant-level",
        entity_category="diagnostic",
    )
    def water_tank_detached(self) -> bool:
        """True if the water tank is detached.

        If water tank is detached, water_level is 127.
        """
        return self.data["water_level"] == 127

    @property
    @sensor(
        "Use Time",
        unit="s",
        device_class="total_increasing",
        icon="mdi:progress-clock",
        entity_category="diagnostic",
    )
    def use_time(self) -> int:
        """Return how long the device has been active in seconds."""
        return self.data["use_time"]

    @property
    def button_pressed(self) -> PressedButton:
        """Return last pressed button."""

        try:
            button = PressedButton(self.data["button_pressed"])
        except ValueError as e:
            _LOGGER.exception("Cannot parse button_pressed: %s", e)
            return PressedButton.No

        return button

    @property
    @sensor(
        "Target Motor Speed",
        unit="rpm",
        device_class="measurement",
        icon="mdi:fast-forward",
        entity_category="diagnostic",
    )
    def motor_speed(self) -> int:
        """Return target speed of the motor."""
        return self.data["speed_level"]

    # Environment

    @property
    @sensor("Temperature", unit="°F", device_class="temperature")
    def fahrenheit(self) -> Optional[float]:
        """Return current temperature in fahrenheit, if available."""
        if self.data["fahrenheit"] is not None:
            return round(self.data["fahrenheit"], 1)
        return None

    # Other

    @property
    @sensor(
        "Power On Time",
        unit="s",
        device_class="total_increasing",
        icon="mdi:progress-clock",
        entity_category="diagnostic",
    )
    def power_time(self) -> int:
        """Return how long the device has been powered in seconds."""
        return self.data["power_time"]


class AirHumidifierMiot(MiotDevice):
    """Main class representing the air humidifier which uses MIoT protocol."""

    _mappings = _MAPPINGS_CA4

    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "Error: {result.error}\n"
            "Target Humidity: {result.target_humidity} %\n"
            "Humidity: {result.humidity} %\n"
            "Temperature: {result.temperature} °C\n"
            "Temperature: {result.fahrenheit} °F\n"
            "Water Level: {result.water_level} %\n"
            "Water tank detached: {result.water_tank_detached}\n"
            "Mode: {result.mode}\n"
            "LED brightness: {result.led_brightness}\n"
            "Buzzer: {result.buzzer}\n"
            "Child lock: {result.child_lock}\n"
            "Dry mode: {result.dry}\n"
            "Button pressed {result.button_pressed}\n"
            "Target motor speed: {result.motor_speed} rpm\n"
            "Actual motor speed: {result.actual_speed} rpm\n"
            "Use time: {result.use_time} s\n"
            "Power time: {result.power_time} s\n"
            "Clean mode: {result.clean_mode}\n",
        )
    )
    def status(self) -> AirHumidifierMiotStatus:
        """Retrieve properties."""

        return AirHumidifierMiotStatus(
            {
                prop["did"]: prop["value"] if prop["code"] == 0 else None
                for prop in self.get_properties_for_mapping()
            }
        )

    @command(default_output=format_output("Powering on"))
    def on(self):
        """Power on."""
        return self.set_property("power", True)

    @command(default_output=format_output("Powering off"))
    def off(self):
        """Power off."""
        return self.set_property("power", False)

    @command(
        click.argument("rpm", type=int),
        default_output=format_output("Setting motor speed '{rpm}' rpm"),
    )
    def set_speed(self, rpm: int):
        """Set motor speed."""
        if rpm < 200 or rpm > 2000 or rpm % 10 != 0:
            raise ValueError(
                "Invalid motor speed: %s. Must be between 200 and 2000 and divisible by 10"
                % rpm
            )
        return self.set_property("speed_level", rpm)

    @command(
        click.argument("humidity", type=int),
        default_output=format_output("Setting target humidity {humidity}%"),
    )
    def set_target_humidity(self, humidity: int):
        """Set target humidity."""
        if humidity < 30 or humidity > 80:
            raise ValueError(
                "Invalid target humidity: %s. Must be between 30 and 80" % humidity
            )
        return self.set_property("target_humidity", humidity)

    @command(
        click.argument("mode", type=EnumType(OperationMode)),
        default_output=format_output("Setting mode to '{mode.value}'"),
    )
    def set_mode(self, mode: OperationMode):
        """Set working mode."""
        return self.set_property("mode", mode.value)

    @command(
        click.argument("brightness", type=EnumType(LedBrightness)),
        default_output=format_output("Setting LED brightness to {brightness}"),
    )
    def set_led_brightness(self, brightness: LedBrightness):
        """Set led brightness."""
        return self.set_property("led_brightness", brightness.value)

    @command(
        click.argument("buzzer", type=bool),
        default_output=format_output(
            lambda buzzer: "Turning on buzzer" if buzzer else "Turning off buzzer"
        ),
    )
    def set_buzzer(self, buzzer: bool):
        """Set buzzer on/off."""
        return self.set_property("buzzer", buzzer)

    @command(
        click.argument("lock", type=bool),
        default_output=format_output(
            lambda lock: "Turning on child lock" if lock else "Turning off child lock"
        ),
    )
    def set_child_lock(self, lock: bool):
        """Set child lock on/off."""
        return self.set_property("child_lock", lock)

    @command(
        click.argument("dry", type=bool),
        default_output=format_output(
            lambda dry: "Turning on dry mode" if dry else "Turning off dry mode"
        ),
    )
    def set_dry(self, dry: bool):
        """Set dry mode on/off."""
        return self.set_property("dry", dry)

    @command(
        click.argument("clean_mode", type=bool),
        default_output=format_output(
            lambda clean_mode: (
                "Turning on clean mode" if clean_mode else "Turning off clean mode"
            )
        ),
    )
    def set_clean_mode(self, clean_mode: bool):
        """Set clean mode on/off."""
        return self.set_property("clean_mode", clean_mode)


class AirHumidifierMiotCA6Status(AirHumidifierMiotCommonStatus):
    """Container for status reports from the air humidifier.

    Xiaomi Smartmi Evaporation Air Humidifier 3 (zhimi.humidifier.ca6) respone (MIoT format)::

        [
            {'did': 'power', 'siid': 2, 'piid': 1, 'code': 0, 'value': True},
            {'did': 'fault', 'siid': 2, 'piid': 2, 'code': 0, 'value': 0},
            {'did': 'mode', 'siid': 2, 'piid': 5, 'code': 0, 'value': 0},
            {'did': 'target_humidity', 'siid': 2, 'piid': 6, 'code': 0, 'value': 50},
            {'did': 'water_level', 'siid': 2, 'piid': 7, 'code': 0, 'value': 1},
            {'did': 'dry', 'siid': 2, 'piid': 8, 'code': 0, 'value': True},
            {'did': 'status', 'siid': 2, 'piid': 9, 'code': 0, 'value': 2},
            {'did': 'temperature', 'siid': 3, 'piid': 7, 'code': 0, 'value': 19.0},
            {'did': 'humidity', 'siid': 3, 'piid': 9, 'code': 0, 'value': 51},
            {'did': 'buzzer', 'siid': 4, 'piid': 1, 'code': 0, 'value': False},
            {'did': 'led_brightness', 'siid': 5, 'piid': 2, 'code': 0, 'value': 2},
            {'did': 'child_lock', 'siid': 6, 'piid': 1, 'code': 0, 'value': False},
            {'did': 'actual_speed', 'siid': 7, 'piid': 1, 'code': 0, 'value': 1100},
            {'did': 'clean_mode', 'siid': 7, 'piid': 5, 'code': 0, 'value': False}
            {'did': 'self_clean_percent, 'siid': 7, 'piid': 6, 'code': 0, 'value': 0},
            {'did': 'pump_state, 'siid': 7, 'piid': 7, 'code': 0, 'value': False},
            {'did': 'pump_cnt', 'siid': 7, 'piid': 8, 'code': 0, 'value': 1000},
        ]
    """

    def __init__(self, data: dict[str, Any]) -> None:
        self.data = data
        super().__init__(self.data)
        self.embed("common", AirHumidifierMiotCommonStatus(self.data))

    # Air Humidifier 3

    @property
    @setting(
        name="Operation Mode",
        setter_name="set_mode",
    )
    def mode(self) -> OperationModeCA6:
        """Return current operation mode."""

        try:
            mode = OperationModeCA6(self.data["mode"])
        except ValueError as e:
            _LOGGER.exception("Cannot parse mode: %s", e)
            return OperationModeCA6.Auto

        return mode

    @property
    @sensor(
        "Water Level",
        unit="%",
        device_class="measurement",
        icon="mdi:water-check",
        entity_category="diagnostic",
    )
    def water_level(self) -> Optional[int]:
        """Return current water level (empty/min, normal, full/max).

        0 - empty/min,  1 - normal, 2 - full/max
        """
        water_level = self.data["water_level"]
        return {0: 0, 1: 50, 2: 100}.get(water_level)

    @property
    @sensor(
        "Operation status",
        device_class="measurement",
        entity_category="diagnostic",
    )
    def status(self) -> OperationStatusCA6:
        """Return current status."""

        try:
            status = OperationStatusCA6(self.data["status"])
        except ValueError as e:
            _LOGGER.exception("Cannot parse status: %s", e)
            return OperationStatusCA6.Close

        return status

    # Other

    @property
    @sensor(
        "Self-clean Percent",
        unit="s",
        device_class="total_increasing",
        icon="mdi:progress-clock",
        entity_category="diagnostic",
    )
    def self_clean_percent(self) -> int:
        """Return time in minutes (from 0 to 30) of self-cleaning procedure."""
        return self.data["self_clean_percent"]

    @property
    @sensor(
        "Pump State",
        entity_category="diagnostic",
    )
    def pump_state(self) -> bool:
        """Return pump state."""
        return self.data["pump_state"]

    @property
    @sensor(
        "Pump Cnt",
        entity_category="diagnostic",
    )
    def pump_cnt(self) -> int:
        """Return pump-cnt."""
        return self.data["pump_cnt"]


class AirHumidifierMiotCA6(MiotDevice):
    """Main class representing zhimi.humidifier.ca6 air humidifier which uses MIoT protocol."""

    _mappings = _MAPPINGS_CA6

    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "Error: {result.error}\n"
            "Target Humidity: {result.target_humidity} %\n"
            "Humidity: {result.humidity} %\n"
            "Temperature: {result.temperature} °C\n"
            "Water Level: {result.water_level} %\n"
            "Mode: {result.mode}\n"
            "Status: {result.status}\n"
            "LED brightness: {result.led_brightness}\n"
            "Buzzer: {result.buzzer}\n"
            "Child lock: {result.child_lock}\n"
            "Dry mode: {result.dry}\n"
            "Actual motor speed: {result.actual_speed} rpm\n"
            "Clean mode: {result.clean_mode}\n"
            "Self clean percent: {result.self_clean_percent} minutes\n"
            "Pump state: {result.pump_state}\n"
            "Pump cnt: {result.pump_cnt}\n",
        )
    )
    def status(self) -> AirHumidifierMiotCA6Status:
        """Retrieve properties."""

        return AirHumidifierMiotCA6Status(
            {
                prop["did"]: prop["value"] if prop["code"] == 0 else None
                for prop in self.get_properties_for_mapping()
            }
        )

    @command(default_output=format_output("Powering on"))
    def on(self):
        """Power on."""
        return self.set_property("power", True)

    @command(default_output=format_output("Powering off"))
    def off(self):
        """Power off."""
        return self.set_property("power", False)

    @command(
        click.argument("humidity", type=int),
        default_output=format_output("Setting target humidity {humidity}%"),
    )
    def set_target_humidity(self, humidity: int):
        """Set target humidity."""
        if humidity < 30 or humidity > 60:
            raise ValueError(
                "Invalid target humidity: %s. Must be between 30 and 60" % humidity
            )
        # HA sends humidity in float, e.g. 45.0
        # ca6 does accept only int values, e.g. 45
        return self.set_property("target_humidity", int(humidity))

    @command(
        click.argument("mode", type=EnumType(OperationModeCA6)),
        default_output=format_output("Setting mode to '{mode.value}'"),
    )
    def set_mode(self, mode: OperationMode):
        """Set working mode."""
        return self.set_property("mode", mode.value)

    @command(
        click.argument("brightness", type=EnumType(LedBrightness)),
        default_output=format_output("Setting LED brightness to {brightness}"),
    )
    def set_led_brightness(self, brightness: LedBrightness):
        """Set led brightness."""
        return self.set_property("led_brightness", brightness.value)

    @command(
        click.argument("buzzer", type=bool),
        default_output=format_output(
            lambda buzzer: "Turning on buzzer" if buzzer else "Turning off buzzer"
        ),
    )
    def set_buzzer(self, buzzer: bool):
        """Set buzzer on/off."""
        return self.set_property("buzzer", buzzer)

    @command(
        click.argument("lock", type=bool),
        default_output=format_output(
            lambda lock: "Turning on child lock" if lock else "Turning off child lock"
        ),
    )
    def set_child_lock(self, lock: bool):
        """Set child lock on/off."""
        return self.set_property("child_lock", lock)

    @command(
        click.argument("dry", type=bool),
        default_output=format_output(
            lambda dry: "Turning on dry mode" if dry else "Turning off dry mode"
        ),
    )
    def set_dry(self, dry: bool):
        """Set dry mode on/off."""
        return self.set_property("dry", dry)

    @command(
        click.argument("clean_mode", type=bool),
        default_output=format_output(
            lambda clean_mode: (
                "Turning on clean mode" if clean_mode else "Turning off clean mode"
            )
        ),
    )
    def set_clean_mode(self, clean_mode: bool):
        """Set clean mode on/off."""
        return self.set_property("clean_mode", clean_mode)
