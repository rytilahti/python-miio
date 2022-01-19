from datetime import timedelta
from enum import Enum
from typing import Any, Dict

from miio import DeviceStatus


class FoodLevel(Enum):
    Normal = 0
    Low = 1
    Empty = 2


class FoodOutletStatus(Enum):
    Ok = 0
    Blocked = 1


class FoodStorageLid(Enum):
    Closed = 0
    Open = 1


class PetFeederStatus(DeviceStatus):
    """Container for status reports from the Pet Feeder / Smart Pet Food Dispenser."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Response from pet feeder (mmgg.feeder.petfeeder):

        {
            "food_level": 0,
            "feed_plan": 1,
            "food_outlet": 0,
            "undeclared": 0,
            "clean_days_left": 11,
            "food_storage_lid": 0,
            "desiccant_days_left": 21,
            "weight_level": 0,
            "wifi_led": 0,
            "button_lock": 1,
            "country_code": 255
        }
        """
        self.data = data

    @property
    def food_level(self) -> FoodLevel:
        """Current food level / status."""
        return FoodLevel(self.data["food_level"])

    @property
    def feed_plan(self) -> bool:
        """Automatic feeding status."""
        return bool(self.data["feed_plan"])

    @property
    def food_outlet(self) -> FoodOutletStatus:
        """Food outlet status."""
        return FoodOutletStatus(self.data["food_outlet"])

    @property
    def food_storage_lid(self) -> FoodStorageLid:
        """Food storage lid status."""
        return FoodStorageLid(self.data["food_storage_lid"])

    @property
    def clean_days_left(self) -> timedelta:
        """Number of days until the unit requires cleaning."""
        return timedelta(days=self.data["clean_days_left"])

    @property
    def desiccant_days_left(self) -> timedelta:
        """Number of days until the desiccant disc requires replacing."""
        return timedelta(days=self.data["desiccant_days_left"])

    @property
    def wifi_led(self) -> bool:
        """WiFi status led."""
        return bool(self.data["wifi_led"])

    @property
    def button_lock(self) -> bool:
        """Lock status for manual dispense button."""
        return bool(self.data["button_lock"] ^ 1)
