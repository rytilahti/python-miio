import pytest

from miio import Device, DeviceException, DeviceFactory, Gateway, MiotDevice

DEVICE_CLASSES = Device.__subclasses__() + MiotDevice.__subclasses__()  # type: ignore
DEVICE_CLASSES.remove(MiotDevice)


def test_device_all_supported_models():
    models = DeviceFactory.supported_models()
    for model, impl in models.items():
        assert isinstance(model, str)
        assert issubclass(impl, Device)


@pytest.mark.parametrize("cls", DEVICE_CLASSES)
def test_device_class_for_model(cls):
    """Test that all supported models can be initialized using class_for_model."""

    if cls == Gateway:
        pytest.skip(
            "Skipping Gateway as AirConditioningCompanion already implements lumi.acpartner.*"
        )

    for supp in cls.supported_models:
        dev = DeviceFactory.class_for_model(supp)
        assert issubclass(dev, cls)


def test_device_class_for_wildcard():
    """Test that wildcard matching works."""

    class _DummyDevice(Device):
        _supported_models = ["foo.bar.*"]

    assert DeviceFactory.class_for_model("foo.bar.aaaa") == _DummyDevice


def test_device_class_for_model_unknown():
    """Test that unknown model raises an exception."""
    with pytest.raises(DeviceException):
        DeviceFactory.class_for_model("foo.foo.xyz")
