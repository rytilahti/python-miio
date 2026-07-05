import enum
from datetime import timedelta
from typing import Any

from miio.devicestatus import sensor, setting
from miio.miot_device import DeviceStatus


class OperatingMode(enum.Enum):
    Normal = 1
    Smart = 2


class PetWaterDispenserStatus(DeviceStatus):
    """Container for status reports from Pet Water Dispenser."""

    def __init__(self, data: dict[str, Any]) -> None:
        """Response of Pet Water Dispenser (mmgg.pet_waterer.s1)
        [
            {'code': 0, 'did': 'cotton_left_time', 'piid': 1, 'siid': 5, 'value': 10},
            {'code': 0, 'did': 'fault', 'piid': 1, 'siid': 2, 'value': 0},
            {'code': 0, 'did': 'filter_left_time', 'piid': 1, 'siid': 3, 'value': 10},
            {'code': 0, 'did': 'indicator_light', 'piid': 1, 'siid': 4, 'value': True},
            {'code': 0, 'did': 'lid_up_flag', 'piid': 4, 'siid': 7, 'value': False},
            {'code': 0, 'did': 'location', 'piid': 2, 'siid': 9, 'value': 'ru'},
            {'code': 0, 'did': 'mode', 'piid': 3, 'siid': 2, 'value': 1},
            {'code': 0, 'did': 'no_water_flag', 'piid': 1, 'siid': 7, 'value': True},
            {'code': 0, 'did': 'no_water_time', 'piid': 2, 'siid': 7, 'value': 0},
            {'code': 0, 'did': 'on', 'piid': 2, 'siid': 2, 'value': True},
            {'code': 0, 'did': 'pump_block_flag', 'piid': 3, 'siid': 7, 'value': False},
            {'code': 0, 'did': 'remain_clean_time', 'piid': 1, 'siid': 6, 'value': 4},
            {'code': 0, 'did': 'timezone', 'piid': 1, 'siid': 9, 'value': 3}
        ]
        """
        self.data = data

    @property
    @sensor(name="Sponge Filter Left Days")
    def sponge_filter_left_days(self) -> timedelta:
        """Filter life time remaining in days."""
        return timedelta(days=self.data["filter_left_time"])

    @property
    def is_on(self) -> bool:
        """True if device is on."""
        return self.data["on"]

    @property
    @setting(
        name="Mode",
        setter_name="set_mode",
        choices=OperatingMode,
    )
    def mode(self) -> OperatingMode:
        """OperatingMode."""
        return OperatingMode(self.data["mode"])

    @property
    @setting(name="LED", setter_name="set_led")
    def is_led_on(self) -> bool:
        """True if enabled."""
        return self.data["indicator_light"]

    @property
    @sensor(name="Cotton Left Days")
    def cotton_left_days(self) -> timedelta:
        """Cotton filter life time remaining in days."""
        return timedelta(days=self.data["cotton_left_time"])

    @property
    @sensor(name="Before Cleaning Days")
    def before_cleaning_days(self) -> timedelta:
        """Days before cleaning."""
        return timedelta(days=self.data["remain_clean_time"])

    @property
    @sensor(name="No Water")
    def is_no_water(self) -> bool:
        """True if there is no water left."""
        if self.data["no_water_flag"]:
            return False
        return True

    @property
    @sensor(name="No Water Duration")
    def no_water_minutes(self) -> timedelta:
        """Minutes without water."""
        return timedelta(minutes=self.data["no_water_time"])

    @property
    @sensor(name="Pump Blocked")
    def is_pump_blocked(self) -> bool:
        """True if pump is blocked."""
        return self.data["pump_block_flag"]

    @property
    @sensor(name="Lid Up")
    def is_lid_up(self) -> bool:
        """True if lid is up."""
        return self.data["lid_up_flag"]

    @property
    @setting(
        name="Timezone",
        setter_name="set_timezone",
        min_value=-12,
        max_value=12,
    )
    def timezone(self) -> int:
        """Timezone from -12 to +12."""
        return self.data["timezone"]

    @property
    @setting(name="Location", setter_name="set_location")
    def location(self) -> str:
        """Device location string."""
        return self.data["location"]

    @property
    @sensor(name="Error Detected")
    def is_error_detected(self) -> bool:
        """True if fault detected."""
        return self.data["fault"] > 0
