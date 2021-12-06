from ..status import FoodStatus, PowerState, PetFoodDispenserStatus

data = {
    "food_status": 0,
    "feed_plan": 1,
    "door_status": 0,
    "feed_today": 0,
    "clean_time": 7,
    "power_status": 0,
    "dryer_days": 6,
    "food_portion": 0,
    "wifi_led": 1,
    "key_lock": 1,
    "country_code": 255,
}

def test_status():
    status = PetFoodDispenserStatus(data)

    assert status.food_status == FoodStatus(0)
    assert status.feed_plan is True
    assert status.door_status is False
    assert status.feed_today == 0
    assert status.clean_time == 7
    assert status.power_status == PowerState(0)
    assert status.dryer_days == 6
    assert status.food_portion == 0
    assert status.wifi_led is True
    assert status.key_lock is False
    assert status.country_code == 255

