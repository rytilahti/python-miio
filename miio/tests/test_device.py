import math

import pytest

from miio import (
    AccessFlags,
    ActionDescriptor,
    DescriptorCollection,
    Device,
    DeviceStatus,
    MiotDevice,
    PropertyDescriptor,
)
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


@pytest.mark.parametrize("cls", DEVICE_CLASSES)
def test_init_signature(cls, mocker):
    """Make sure that __init__ of every device-inheriting class accepts the expected
    parameters."""
    mocker.patch("miio.Device.send")
    parent_init = mocker.spy(Device, "__init__")
    kwargs = {
        "ip": "IP",
        "token": None,
        "start_id": 0,
        "debug": False,
        "lazy_discover": True,
        "timeout": None,
        "model": None,
    }
    cls(**kwargs)

    # A rather hacky way to check for the arguments, we cannot use assert_called_with
    # as some arguments are passed by inheriting classes using kwargs
    total_args = len(parent_init.call_args.args) + len(parent_init.call_args.kwargs)
    assert total_args == 8


@pytest.mark.parametrize("cls", DEVICE_CLASSES)
def test_status_return_type(cls):
    """Make sure that all status methods have a type hint."""
    assert "return" in cls.status.__annotations__
    assert issubclass(cls.status.__annotations__["return"], DeviceStatus)


def test_supports_miot(mocker):
    from miio.exceptions import DeviceError

    send = mocker.patch(
        "miio.Device.send", side_effect=DeviceError({"code": 1, "message": 1})
    )
    d = Device("127.0.0.1", "68ffffffffffffffffffffffffffffff")
    assert d.supports_miot() is False

    send.side_effect = None
    assert d.supports_miot() is True


@pytest.mark.parametrize("getter_name", ["actions", "settings", "sensors"])
def test_cached_descriptors(getter_name, mocker, caplog):
    d = Device("127.0.0.1", "68ffffffffffffffffffffffffffffff")
    getter = getattr(d, getter_name)
    initialize_descriptors = mocker.spy(d, "_initialize_descriptors")
    mocker.patch("miio.Device.send")
    patched_status = mocker.patch("miio.Device.status")
    patched_status.__annotations__ = {}
    patched_status.__annotations__["return"] = DeviceStatus
    mocker.patch.object(d._descriptors, "descriptors_from_object", return_value={})
    for _i in range(5):
        getter()
    initialize_descriptors.assert_called_once()
    assert (
        "'Device' does not specify any descriptors, please considering creating a PR"
        in caplog.text
    )


def test_change_setting(mocker):
    """Test setting changing."""
    d = Device("127.0.0.1", "68ffffffffffffffffffffffffffffff")
    mocker.patch("miio.Device.send")
    mocker.patch("miio.Device.send_handshake")

    descs = {
        "read-only": PropertyDescriptor(
            id="ro", name="ro", status_attribute="ro", access=AccessFlags.Read
        ),
        "write-only": PropertyDescriptor(
            id="wo", name="wo", status_attribute="wo", access=AccessFlags.Write
        ),
    }
    writable = descs["write-only"]
    coll = DescriptorCollection(descs, device=d)

    mocker.patch.object(d, "descriptors", return_value=coll)

    # read-only descriptors should not appear in settings
    assert len(d.settings()) == 1

    # trying to change non-existing setting should raise an error
    with pytest.raises(
        ValueError, match="Unable to find setting 'non-existing-setting'"
    ):
        d.change_setting("non-existing-setting")

    # calling change setting should call the setter of the descriptor
    setter = mocker.patch.object(writable, "setter")
    d.change_setting("write-only", "new value")
    setter.assert_called_with("new value")


def test_call_action(mocker):
    """Test action calling."""
    d = Device("127.0.0.1", "68ffffffffffffffffffffffffffffff")
    mocker.patch("miio.Device.send")
    mocker.patch("miio.Device.send_handshake")

    descs = {
        "read-only": PropertyDescriptor(
            id="ro", name="ro", status_attribute="ro", access=AccessFlags.Read
        ),
        "write-only": PropertyDescriptor(
            id="wo", name="wo", status_attribute="wo", access=AccessFlags.Write
        ),
        "action": ActionDescriptor(id="foo", name="action"),
    }
    act = descs["action"]
    coll = DescriptorCollection(descs, device=d)

    mocker.patch.object(d, "descriptors", return_value=coll)

    # property descriptors should not appear in actions
    assert len(d.actions()) == 1

    # trying to execute non-existing action should raise an error
    with pytest.raises(ValueError, match="Unable to find action 'non-existing-action'"):
        d.call_action("non-existing-action")

    method = mocker.patch.object(act, "method")
    d.call_action("action", "testinput")
    method.assert_called_with("testinput")
    method.reset_mock()

    # Calling without parameters executes a different code path
    d.call_action("action")
    method.assert_called_once()
