from unittest import TestCase

from miio import Action, DeviceSpec, Property, Service, SpecificationType, UrnExpression


class TestUrnExpression(TestCase):
    def test_parsing_valid_expression(self):
        expression = "urn:miot-spec-v2:property:motor-control:00000038:dmaker-p11:1"
        urn_expression = UrnExpression(expression)
        assert urn_expression.namespace == "miot-spec-v2"
        assert urn_expression.type == SpecificationType.Property
        assert urn_expression.name == "motor-control"
        assert urn_expression.value == "00000038"
        assert urn_expression.vendor_product == "dmaker-p11"
        assert urn_expression.version == 1


class TestDevice(TestCase):
    def test_parsing_device(self):
        spec = """
        {
          "type": "urn:miot-spec-v2:device:fan:0000A005:dmaker-p11:1",
          "description": "Fan",
          "services": []
        }
        """
        device = DeviceSpec.from_json(spec)
        assert device.description == "Fan"
        assert device.type.name == "fan"

    def test_find_service(self):
        spec = """
        {
          "type": "urn:miot-spec-v2:device:fan:0000A005:dmaker-p11:1",
          "description": "Fan",
          "services": [
            {
              "iid": 2,
              "type": "urn:miot-spec-v2:service:fan:00007808:dmaker-p11:1",
              "description": "Fan",
              "properties": []
            }
          ]
        }
        """
        device = DeviceSpec.from_json(spec)
        fan_service = device.find_service("fan")
        assert fan_service.iid == 2


class TestService(TestCase):
    def test_parsing_service(self):
        json = """
        {
          "iid": 2,
          "type": "urn:miot-spec-v2:service:fan:00007808:dmaker-p11:1",
          "description": "Fan",
          "properties": []
        }
        """
        service = Service.from_json(json)
        assert service.description == "Fan"

    def test_find_property(self):
        json = """
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
        """
        service = Service.from_json(json)
        p = service.find_property("on")
        assert p.iid == 1
        assert len(p.access) == 3

    def test_load(self):
        device = DeviceSpec.load(
            "urn:miot-spec-v2:device:fan:0000A005:dmaker-p10:1.json"
        )
        assert device.type.name == "fan"


class TestProperty(TestCase):
    def test_parsing_property(self):
        json = """
        {
          "iid": 2,
          "type": "urn:miot-spec-v2:property:fan-level:00000016:dmaker-p11:1",
          "description": "Gear Fan Level ",
          "format": "uint8",
          "access": [
            "read",
            "write",
            "notify"
          ],
          "unit": "none",
          "value-list": [
            {
              "value": 1,
              "description": "Level1"
            },
            {
              "value": 2,
              "description": "Level2"
            },
            {
              "value": 3,
              "description": "Level3"
            },
            {
              "value": 4,
              "description": "Level4"
            }
          ]
        }
        """
        property = Property.from_json(json)
        assert len(property.access) == 3
        assert len(property.value_list) == 4
        assert property.type.type == SpecificationType.Property


class TestAction(TestCase):
    def test_parsing_action(self):
        json = """
        {
          "iid": 1,
          "type": "urn:dmaker-spec:action:toggle:00002801:dmaker-p11:1",
          "description": "toggle",
          "in": [],
          "out": []
        }
        """
        action = Action.from_json(json)
        assert action.iid == 1
