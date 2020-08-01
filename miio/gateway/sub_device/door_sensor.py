"""Xiaomi Zigbee door sensor."""

from .sub_device import SubDevice


class Magnet(SubDevice):
    """Subdevice Magnet specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.sensor_magnet"
    _model = "MCCGQ01LM"
    _name = "Door sensor"


class AqaraMagnet(SubDevice):
    """Subdevice AqaraMagnet specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.sensor_magnet.aq2"
    _model = "MCCGQ11LM"
    _name = "Door sensor"
