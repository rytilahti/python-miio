from datetime import time

import pytest

from miio.tests.dummies import DummyDevice

from .viomiwaterheater import (
    MODEL_WATERHEATER_E1,
    OperationMode,
    OperationStatus,
    ViomiWaterHeater,
    ViomiWaterHeaterException,
    ViomiWaterHeaterStatus,
)


class DummyViomiWaterHeater(DummyDevice, ViomiWaterHeater):
    def __init__(self, *args, **kwargs):
        self._model = MODEL_WATERHEATER_E1
        self.state = {
            "washStatus": 1,
            "power": 1,
            "velocity": 0,
            "waterTemp": 29,
            "targetTemp": 70,
            "errStatus": 0,
            "hotWater": 60,
            "needClean": 0,
            "modeType": 1,
            "appointStart": 7,
            "appointEnd": 12,
        }
        self.return_values = {
            "get_prop": self._get_state,
            "set_power": lambda x: self._set_state("power", x),
            "set_temp": lambda x: self._set_state("targetTemp", x),
            "set_mode": lambda x: self._set_state("modeType", x),
            "set_appoint": lambda x: self._set_state("appoint", x),
        }
        super().__init__(*args, **kwargs)


@pytest.fixture
def viomiwaterheater(request):
    return DummyViomiWaterHeater()


def test_status(viomiwaterheater: DummyViomiWaterHeater):
    status = viomiwaterheater.status()
    assert isinstance(status, ViomiWaterHeaterStatus)
    assert status.status == OperationStatus.Heating
    assert status.is_on is True
    assert status.velocity == 0
    assert status.water_temperature == 29
    assert status.target_temperature == 70
    assert status.error == 0
    assert status.hot_water_volume == 60
    assert status.cleaning_required is False
    assert status.mode == OperationMode.Heating
    assert status.service_time_start == time(7)
    assert status.service_time_end == time(12)


def test_on(viomiwaterheater: DummyViomiWaterHeater):
    viomiwaterheater.on()
    assert viomiwaterheater.state["power"] == 1


def test_off(viomiwaterheater: DummyViomiWaterHeater):
    viomiwaterheater.off()
    assert viomiwaterheater.state["power"] == 0


def test_set_target_temperature(viomiwaterheater: DummyViomiWaterHeater):
    viomiwaterheater.set_target_temperature(50)
    assert viomiwaterheater.state["targetTemp"] == 50

    with pytest.raises(ViomiWaterHeaterException):
        viomiwaterheater.set_target_temperature(20)

    with pytest.raises(ViomiWaterHeaterException):
        viomiwaterheater.set_target_temperature(80)


def test_set_mode(viomiwaterheater: DummyViomiWaterHeater):
    viomiwaterheater.set_mode(OperationMode.Thermostatic)
    assert viomiwaterheater.state["modeType"] == 0

    viomiwaterheater.set_mode(OperationMode.Booking)
    # Booking mode sets appoint with [1, appointStart, appointEnd], popping 1 into appoint
    assert viomiwaterheater.state["appoint"] == 1


def test_set_service_time(viomiwaterheater: DummyViomiWaterHeater):
    viomiwaterheater.set_service_time(8, 14)
    # set_service_time sends [0, 8, 14], popping 0 into appoint
    assert viomiwaterheater.state["appoint"] == 0

    with pytest.raises(ViomiWaterHeaterException):
        viomiwaterheater.set_service_time(-1, 10)

    with pytest.raises(ViomiWaterHeaterException):
        viomiwaterheater.set_service_time(10, 25)
