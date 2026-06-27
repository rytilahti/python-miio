import enum
from datetime import time
from typing import Any, Optional

from miio.miot_device import DeviceStatus


class PetFountainStatus(enum.Enum):
    """The fountain operating status."""

    NoWater = "no_water"
    Watering = "watering"


class PetFountainMode(enum.Enum):
    """The fountain water mode."""

    Auto = "auto"
    Interval = "interval"
    Continuous = "continuous"


class ChargingState(enum.Enum):
    """The fountain charging state."""

    NotCharging = "not_charging"
    Charging = "charging"
    Charged = "charged"


class XiaomiPetFountainStatus(DeviceStatus):
    """Container for status reports from Xiaomi Pet Fountain 2."""

    def __init__(self, data: dict[str, Any]) -> None:
        """Initialize the status container."""
        self.data = data

    @property
    def is_on(self) -> bool:
        """Return true to keep option entities available."""
        return True

    @property
    def fault_code(self) -> Optional[int]:
        """Return the raw fault code."""
        raw_fault = self.data.get("fault_code")
        if not isinstance(raw_fault, int):
            return None
        return raw_fault

    @property
    def has_fault(self) -> bool:
        """Return true when the device reports a fault."""
        code = self.fault_code
        return code is not None and code > 0

    @property
    def status(self) -> Optional[PetFountainStatus]:
        """Return the fountain operating status."""
        raw_status = self.data.get("status")
        if not isinstance(raw_status, int):
            return None
        return {
            1: PetFountainStatus.NoWater,
            2: PetFountainStatus.Watering,
        }.get(raw_status)

    @property
    def mode(self) -> Optional[PetFountainMode]:
        """Return the configured water mode."""
        raw_mode = self.data.get("mode")
        if not isinstance(raw_mode, int):
            return None
        return {
            0: PetFountainMode.Auto,
            1: PetFountainMode.Interval,
            2: PetFountainMode.Continuous,
        }.get(raw_mode)

    @property
    def water_interval(self) -> Optional[int]:
        """Return the configured water interval in minutes."""
        return self.data.get("water_interval")

    @property
    def water_shortage(self) -> Optional[bool]:
        """Return true when the fountain is low on water."""
        return self.data.get("water_shortage")

    @property
    def filter_life_remaining(self) -> Optional[int]:
        """Return the remaining filter life in percent."""
        return self.data.get("filter_life_remaining")

    @property
    def filter_left_time(self) -> Optional[float]:
        """Return the remaining filter time in days."""
        value = self.data.get("filter_left_time")
        if value is None:
            return None
        return round(value / 24, 2)

    @property
    def child_lock(self) -> Optional[bool]:
        """Return true when physical controls are locked."""
        return self.data.get("child_lock")

    @property
    def battery(self) -> Optional[int]:
        """Return battery level percentage."""
        return self.data.get("battery")

    @property
    def charging_state(self) -> Optional[ChargingState]:
        """Return the charging state."""
        raw_state = self.data.get("charging_state")
        if not isinstance(raw_state, int):
            return None
        return {
            0: ChargingState.NotCharging,
            1: ChargingState.Charging,
            2: ChargingState.Charged,
        }.get(raw_state)

    @property
    def do_not_disturb(self) -> Optional[bool]:
        """Return true when do not disturb is enabled."""
        return self.data.get("do_not_disturb")

    @property
    def low_battery(self) -> Optional[bool]:
        """Return true when the device reports low battery."""
        return self.data.get("low_battery")

    @property
    def usb_power(self) -> Optional[bool]:
        """Return true when USB power is connected."""
        return self.data.get("usb_power")

    @property
    def dnd_start(self) -> Optional[time]:
        """Return the DnD start time."""
        value = self.data.get("dnd_start")
        if value is None:
            return None
        return _seconds_to_time(value)

    @property
    def dnd_end(self) -> Optional[time]:
        """Return the DnD end time."""
        value = self.data.get("dnd_end")
        if value is None:
            return None
        return _seconds_to_time(value)

    @property
    def pump_blocked(self) -> Optional[bool]:
        """Return true when the pump is blocked."""
        return self.data.get("pump_blocked")


def _seconds_to_time(value: int) -> time:
    value %= 24 * 60 * 60
    hours, remainder = divmod(value, 3600)
    minutes, seconds = divmod(remainder, 60)
    return time(hour=hours, minute=minutes, second=seconds)


def _time_to_seconds(value: time) -> int:
    return value.hour * 3600 + value.minute * 60 + value.second
