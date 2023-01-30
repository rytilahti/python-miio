import json
from pathlib import Path

import pytest
from micloud.micloudexception import MiCloudAccessDenied

from miio import CloudException, CloudInterface


def load_fixture(filename: str) -> str:
    """Load a fixture."""
    file = Path(__file__).parent.absolute() / "fixtures" / filename
    with file.open() as f:
        return json.load(f)


MICLOUD_DEVICES_RESPONSE = load_fixture("micloud_devices_response.json")


@pytest.fixture
def cloud() -> CloudInterface:
    """Cloud interface fixture."""

    return CloudInterface(username="foo", password="bar")


def test_available_locales(cloud: CloudInterface):
    """Test available locales."""
    available = cloud.available_locales()
    assert list(available.keys()) == ["all", "cn", "de", "i2", "ru", "sg", "us"]


def test_login_success(cloud: CloudInterface, mocker):
    """Test cloud login success."""
    login = mocker.patch("micloud.MiCloud.login", return_value=True)
    cloud._login()
    login.assert_called()


@pytest.mark.parametrize(
    "mock_params",
    [{"side_effect": MiCloudAccessDenied("msg")}, {"return_value": False}],
)
def test_login(cloud: CloudInterface, mocker, mock_params):
    """Test cloud login failures."""
    mocker.patch("micloud.MiCloud.login", **mock_params)
    with pytest.raises(CloudException):
        cloud._login()


def test_single_login_for_all_locales(cloud: CloudInterface, mocker):
    """Test that login gets called only once."""
    login = mocker.patch("micloud.MiCloud.login", return_value=True)
    mocker.patch("micloud.MiCloud.get_devices", return_value=MICLOUD_DEVICES_RESPONSE)
    cloud.get_devices()
    login.assert_called_once()


@pytest.mark.parametrize("locale", CloudInterface.available_locales())
def test_get_devices(cloud: CloudInterface, locale, mocker):
    """Test cloud get devices."""
    login = mocker.patch("micloud.MiCloud.login", return_value=True)
    mocker.patch("micloud.MiCloud.get_devices", return_value=MICLOUD_DEVICES_RESPONSE)

    devices = cloud.get_devices(locale)

    multiplier = len(CloudInterface.available_locales()) - 1 if locale == "all" else 1
    assert len(devices) == 3 * multiplier

    main_devs = [dev for dev in devices.values() if not dev.is_child]
    assert len(main_devs) == 2 * multiplier

    dev = list(devices.values())[0]

    if locale != "all":
        assert dev.locale == locale

    login.assert_called_once()


def test_cloud_device_info(cloud: CloudInterface, mocker):
    """Test cloud device info."""
    mocker.patch("micloud.MiCloud.login", return_value=True)
    mocker.patch("micloud.MiCloud.get_devices", return_value=MICLOUD_DEVICES_RESPONSE)

    devices = cloud.get_devices("de")
    dev = list(devices.values())[0]

    assert dev.raw_data == MICLOUD_DEVICES_RESPONSE[0]
    assert dev.name == "device 1"
    assert dev.mac == "xx:xx:xx:xx:xx:xx"
    assert dev.model == "some.model.v2"
    assert dev.is_child is False
    assert dev.parent_id == ""
    assert dev.parent_model == ""
    assert dev.is_online is False
    assert dev.did == "1234"
    assert dev.ssid == "ssid"
    assert dev.bssid == "xx:xx:xx:xx:xx:xx"
    assert dev.description == "description"
    assert dev.locale == "de"
    assert dev.rssi == -55
