from datetime import timedelta

from ..status import FoodLevel, FoodOutletStatus, FoodStorageLid, PetFeederStatus

data = {
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
    "country_code": 255,
}


def test_status():
    status = PetFeederStatus(data)

    assert status.food_level == FoodLevel(0)
    assert status.feed_plan is True
    assert status.food_outlet == FoodOutletStatus(0)
    assert status.clean_days_left == timedelta(days=11)
    assert status.food_storage_lid == FoodStorageLid(0)
    assert status.desiccant_days_left == timedelta(days=21)
    assert status.wifi_led is False
    assert status.button_lock is False
