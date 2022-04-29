import math

import pytest

from miio import Device, MiotDevice, RoborockVacuum
from miio.exceptions import DeviceInfoUnavailableException, PayloadDecodeException

DEVICE_CLASSES = Device.__subclasses__() + MiotDevice.__subclasses__()  # type: ignore
DEVICE_CLASSES.remove(MiotDevice)


@pytest.mark.parametrize("max_properties", [None, 1, 15])
def test_get_properties_splitting(mocker, max_properties):
    properties = [i for i in range(20)]

    send = mocker.patch("miio.Device.send")
    d = Device("127.0.0.1", "68ffffffffffffffffffffffffffffff")
    d.get_properties(properties, max_properties=max_properties)

    if max_properties is None:
        max_properties = len(properties)
    assert send.call_count == math.ceil(len(properties) / max_properties)


def test_default_timeout_and_retry(mocker):
    send = mocker.patch("miio.miioprotocol.MiIOProtocol.send")
    d = Device("127.0.0.1", "68ffffffffffffffffffffffffffffff")
    assert d._protocol._timeout == 5
    d.send(command="fake_command", parameters=[])
    send.assert_called_with("fake_command", [], 3, extra_parameters=None)


def test_timeout_retry(mocker):
    send = mocker.patch("miio.miioprotocol.MiIOProtocol.send")
    d = Device("127.0.0.1", "68ffffffffffffffffffffffffffffff", timeout=4)
    assert d._protocol._timeout == 4
    d.send("fake_command", [], 1)
    send.assert_called_with("fake_command", [], 1, extra_parameters=None)
    d.send("fake_command", [])
    send.assert_called_with("fake_command", [], 3, extra_parameters=None)

    class CustomDevice(Device):
        retry_count = 5
        timeout = 1

    d2 = CustomDevice("127.0.0.1", "68ffffffffffffffffffffffffffffff")
    assert d2._protocol._timeout == 1
    d2.send("fake_command", [])
    send.assert_called_with("fake_command", [], 5, extra_parameters=None)


def test_unavailable_device_info_raises(mocker):
    """Make sure custom exception is raised if the info payload is invalid."""
    send = mocker.patch("miio.Device.send", side_effect=PayloadDecodeException)
    d = Device("127.0.0.1", "68ffffffffffffffffffffffffffffff")

    with pytest.raises(DeviceInfoUnavailableException):
        d.info()

    assert send.call_count == 1


def test_device_id_handshake(mocker):
    """Make sure send_handshake() gets called if did is unknown."""
    handshake = mocker.patch("miio.Device.send_handshake")
    _ = mocker.patch("miio.Device.send")

    d = Device("127.0.0.1", "68ffffffffffffffffffffffffffffff")

    d.device_id

    handshake.assert_called()


def test_device_id(mocker):
    """Make sure send_handshake() does not get called if did is already known."""
    handshake = mocker.patch("miio.Device.send_handshake")
    _ = mocker.patch("miio.Device.send")

    d = Device("127.0.0.1", "68ffffffffffffffffffffffffffffff")
    d._protocol._device_id = b"12345678"

    d.device_id

    handshake.assert_not_called()


def test_model_autodetection(mocker):
    """Make sure info() gets called if the model is unknown."""
    info = mocker.patch("miio.Device._fetch_info")
    _ = mocker.patch("miio.Device.send")

    d = Device("127.0.0.1", "68ffffffffffffffffffffffffffffff")

    d.raw_command("cmd", {})

    info.assert_called()


def test_forced_model(mocker):
    """Make sure info() does not get called automatically if model is given."""
    info = mocker.patch("miio.Device.info")
    _ = mocker.patch("miio.Device.send")

    DUMMY_MODEL = "dummy.model"

    d = Device("127.0.0.1", "68ffffffffffffffffffffffffffffff", model=DUMMY_MODEL)
    d.raw_command("dummy", {})

    assert d.model == DUMMY_MODEL
    info.assert_not_called()


@pytest.mark.parametrize(
    "cls,hidden", [(Device, True), (MiotDevice, True), (RoborockVacuum, False)]
)
def test_missing_supported(mocker, caplog, cls, hidden):
    """Make sure warning is logged if the device is unsupported for the class."""
    _ = mocker.patch("miio.Device.send")

    d = cls("127.0.0.1", "68ffffffffffffffffffffffffffffff")
    d._fetch_info()

    if hidden:
        assert "Found an unsupported model" not in caplog.text
        assert f"for class '{cls.__name__}'" not in caplog.text
    else:
        assert "Found an unsupported model" in caplog.text
        assert f"for class '{cls.__name__}'" in caplog.text


@pytest.mark.parametrize("cls", DEVICE_CLASSES)
def test_device_ctor_model(cls):
    """Make sure that every device subclass ctor accepts model kwarg."""
    # TODO Huizuo implements custom model fallback, so it needs to be ignored for now
    ignore_classes = ["GatewayDevice", "CustomDevice", "Huizuo"]
    if cls.__name__ in ignore_classes:
        return

    dummy_model = "dummy"
    dev = cls("127.0.0.1", "68ffffffffffffffffffffffffffffff", model=dummy_model)
    assert dev.model == dummy_model


@pytest.mark.parametrize("cls", DEVICE_CLASSES)
def test_device_supported_models(cls):
    """Make sure that every device subclass has a non-empty supported models."""
    assert cls.supported_models
