import enum
from typing import Any, Dict

from miio import DeviceStatus

class FoodStatus(enum.Enum):
    Normal = 0
    Low = 1
    Empty = 2

class PowerState(enum.Enum):
    Mains = 0
    Battery = 1

class PetFoodDispenserStatus(DeviceStatus):
    """Container for status reports from the Pet Feeder / Smart Pet Food Dispenser."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Response from pet feeder (mmgg.feeder.petfeeder):
 
        {'food_status': 0, 'feed_plan': 1, 'door_status': 0,
          'feed_today': 0, 'clean_time': 7, 'power_status': 0,
          'dryer_days': 6, 'food_portion': 0, 'wifi_led': 1,
          'key_lock': 1, 'country_code': 255,}
        """
        self.data = data

    @property
    def food_status(self) -> str:
        """Current food status / level."""
        return FoodStatus(self.data["food_status"])

    @property
    def feed_plan(self) -> bool:
        """Automatic feeding status."""
        return bool(self.data["feed_plan"])

    @property
    def door_status(self) -> bool:
        """Food bin door status."""
        return bool(self.data["door_status"])

    @property
    def clean_days(self) -> int:
        """Number of days until the unit requires cleaning."""
        return self.data['clean_days']

    @property
    def power_status(self) -> str:
        """Power status."""
        return PowerState(self.data["power_status"])

    @property
    def dryer_days(self) -> int:
        """Number of days until the desiccant disc requires replacing."""
        return self.data['dryer_days']

    @property
    def wifi_led(self) -> bool:
        """WiFi LED Status."""
        return bool(self.data["wifi_led"])

    @property
    def key_lock(self) -> bool:
        """Key lock status for manual dispense button."""
        return bool(self.data["key_lock"])

    @property
    def county_code(self) -> int:
        """Device country code."""
        raise NotImplementedError("Device does not currently return this value correctly.")


