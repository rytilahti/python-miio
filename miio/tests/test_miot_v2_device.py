from unittest import TestCase

import pytest

from miio import DeviceSpec, MiotV2Device


@pytest.fixture(scope="class")
def miot_v2_device(request):
    json = """
    {
      "type": "urn:miot-spec-v2:device:fan:0000A005:dmaker-p11:1",
      "description": "Fan",
      "services": [
        {
          "iid": 2,
          "type": "urn:miot-spec-v2:service:fan:00007808:dmaker-p11:1",
          "description": "Fan",
          "properties": [
            {
              "iid": 1,
              "type": "urn:miot-spec-v2:property:on:00000006:dmaker-p11:1",
              "description": "Switch Status",
              "format": "bool",
              "access": [
                "read",
                "write",
                "notify"
              ]
            }
          ]
        }
      ]
    }
    """
    spec = DeviceSpec.from_json(json)
    request.cls.device = MiotV2Device(
        spec, "127.0.0.1", "68ffffffffffffffffffffffffffffff"
    )


@pytest.mark.usefixtures("miot_v2_device")
class TestMiotV2Device(TestCase):
    @pytest.fixture(autouse=True)
    def __inject_fixtures(self, mocker):
        self.mocker = mocker

    def test_get_readable_properties(self):
        device = self.device
        self.mocker.patch.object(
            device,
            "get_properties",
            return_value=[
                {"did": "fan.on", "siid": 2, "piid": 1, "code": 0, "value": False}
            ],
            autospec=True,
        )
        properties = device.get_readable_properties()
        assert len(properties) == 1
        device.get_properties.assert_called_once_with(
            [{"did": "fan.on", "siid": 2, "piid": 1}],
            property_getter="get_properties",
            max_properties=15,
        )

    def test_set_property(self):
        device = self.device
        self.mocker.patch.object(device, "send", autospec=True)
        device.set_property("fan", "on", False)
        device.send.assert_called_once_with(
            "set_properties", [{"did": "fan.on", "siid": 2, "piid": 1, "value": False}]
        )


class Foo:
    p1: str
    p2: str

    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
