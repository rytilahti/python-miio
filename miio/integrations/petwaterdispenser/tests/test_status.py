from datetime import timedelta

from ..status import OperatingMode, PetWaterDispenserStatus

data = {
    "cotton_left_time": 10,
    "fault": 0,
    "filter_left_time": 10,
    "indicator_light": True,
    "lid_up_flag": False,
    "location": "ru",
    "mode": 1,
    "no_water_flag": True,
    "no_water_time": 0,
    "on": True,
    "pump_block_flag": False,
    "remain_clean_time": 2,
    "timezone": 3,
}


def test_status():
    status = PetWaterDispenserStatus(data)

    assert status.is_on is True
    assert status.sponge_filter_left_days == timedelta(days=10)
    assert status.mode == OperatingMode(1)
    assert status.is_led_on is True
    assert status.cotton_left_days == timedelta(days=10)
    assert status.before_cleaning_days == timedelta(days=2)
    assert status.is_no_water is False
    assert status.no_water_minutes == timedelta(minutes=0)
    assert status.is_pump_blocked is False
    assert status.is_lid_up is False
    assert status.timezone == 3
    assert status.location == "ru"
    assert status.is_error_detected is False
