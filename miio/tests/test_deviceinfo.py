import pytest

from miio.deviceinfo import DeviceInfo


@pytest.fixture()
def info():
    """Example response from Xiaomi Smart WiFi Plug (c&p from deviceinfo ctor)."""
    return DeviceInfo(
        {
            "ap": {"bssid": "FF:FF:FF:FF:FF:FF", "rssi": -68, "ssid": "network"},
            "cfg_time": 0,
            "fw_ver": "1.2.4_16",
            "hw_ver": "MW300",
            "life": 24,
            "mac": "28:FF:FF:FF:FF:FF",
            "mmfree": 30312,
            "model": "chuangmi.plug.m1",
            "netif": {
                "gw": "192.168.xxx.x",
                "localIp": "192.168.xxx.x",
                "mask": "255.255.255.0",
            },
            "ot": "otu",
            "ott_stat": [0, 0, 0, 0],
            "otu_stat": [320, 267, 3, 0, 3, 742],
            "token": "2b00042f7481c7b056c4b410d28f33cf",
            "wifi_fw_ver": "SD878x-14.76.36.p84-702.1.0-WM",
        }
    )


def test_properties(info):
    """Test that all deviceinfo properties are accessible."""

    assert info.raw == info.data

    assert isinstance(info.accesspoint, dict)
    assert isinstance(info.network_interface, dict)

    ap_props = ["bssid", "ssid", "rssi"]
    for prop in ap_props:
        assert prop in info.accesspoint

    if_props = ["gw", "localIp", "mask"]
    for prop in if_props:
        assert prop in info.network_interface

    assert info.model is not None
    assert info.firmware_version is not None
    assert info.hardware_version is not None
    assert info.mac_address is not None


def test_missing_fields(info):
    """Test that missing keys do not cause exceptions."""
    for k in ["fw_ver", "hw_ver", "model", "token", "mac"]:
        del info.raw[k]

    assert info.model is None
    assert info.firmware_version is None
    assert info.hardware_version is None
    assert info.mac_address is None
    assert info.token is None


def test_cli_output(info, mocker):
    mocker.patch("miio.Device.send")
    mocker.patch("miio.Device.supports_miot", return_value=False)

    output = info.__cli_output__
    assert "Model: chuangmi.plug.m1" in output
    assert "Hardware version: MW300" in output
    assert "Firmware version: 1.2.4_16" in output
    assert "Supported using: ChuangmiPlug" in output
    assert "Command: miiocli chuangmiplug" in output
    assert "Supported by genericmiot: False" in output
