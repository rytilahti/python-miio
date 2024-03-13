import pytest

from ..device import Device
from ..devicestatus import DeviceStatus, action, sensor, setting


@pytest.fixture()
def dummy_status():
    """Fixture for a status class with different sensors and settings."""

    class Status(DeviceStatus):
        @property
        @sensor("sensor_without_unit")
        def sensor_without_unit(self) -> int:
            return 1

        @property
        @sensor("sensor_with_unit", unit="V")
        def sensor_with_unit(self) -> int:
            return 2

        @property
        @setting("setting_without_unit", setter_name="dummy")
        def setting_without_unit(self):
            return 3

        @property
        @setting("setting_with_unit", unit="V", setter_name="dummy")
        def setting_with_unit(self):
            return 4

        @property
        @sensor("none_sensor")
        def sensor_returning_none(self):
            return None

    yield Status()


@pytest.fixture()
def dummy_device(mocker, dummy_status):
    """Returns a very basic device with patched out I/O and a dummy status."""

    class DummyDevice(Device):
        @action(id="test", name="test")
        def test_action(self):
            pass

    d = DummyDevice("127.0.0.1", "68ffffffffffffffffffffffffffffff")
    d._protocol._device_id = b"12345678"
    mocker.patch("miio.Device.send")
    mocker.patch("miio.Device.send_handshake")

    patched_status = mocker.patch("miio.Device.status")
    patched_status.__annotations__ = {}
    patched_status.__annotations__["return"] = dummy_status

    yield d
