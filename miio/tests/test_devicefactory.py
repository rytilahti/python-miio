import pytest

from miio import Device, DeviceFactory, DeviceInfo, Gateway, GenericMiot, MiotDevice

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
    """Test that unknown model returns genericmiot."""
    assert DeviceFactory.class_for_model("foo.foo.xyz.invalid") == GenericMiot


@pytest.mark.parametrize("cls", DEVICE_CLASSES)
@pytest.mark.parametrize("force_model", [True, False])
def test_create(cls, force_model, mocker):
    """Test create for both forced and autodetected models."""
    mocker.patch("miio.Device.send")

    model = None
    first_supported_model = next(iter(cls.supported_models))
    if force_model:
        model = first_supported_model

    dummy_info = DeviceInfo({"model": first_supported_model})
    info = mocker.patch("miio.Device.info", return_value=dummy_info)

    device = DeviceFactory.create("127.0.0.1", 32 * "0", model=model)
    device_class = DeviceFactory.class_for_model(device.model)
    assert isinstance(device, device_class)

    if force_model:
        info.assert_not_called()
    else:
        info.assert_called()


@pytest.mark.parametrize("cls", DEVICE_CLASSES)
def test_create_force_miot(cls, mocker):
    """Test that force_generic_miot works."""
    mocker.patch("miio.Device.send")
    mocker.patch("miio.Device.info")
    class_for_model = mocker.patch("miio.DeviceFactory.class_for_model")

    assert isinstance(
        DeviceFactory.create("127.0.0.1", 32 * "0", force_generic_miot=True),
        GenericMiot,
    )

    class_for_model.assert_not_called()
