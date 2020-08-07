"""Xiaomi Zigbee door sensor."""

from .sub_device import SubDevice


class MagnetDevice(SubDevice):
    """Base class for subdevice magnet."""

    properties = []


class Magnet(MagnetDevice):
    """Subdevice Magnet specific properties and methods."""

    _zigbee_model = "lumi.sensor_magnet"
    _model = "MCCGQ01LM"
    _name = "Door sensor"


class AqaraMagnet(MagnetDevice):
    """Subdevice AqaraMagnet specific properties and methods."""

    _zigbee_model = "lumi.sensor_magnet.aq2"
    _model = "MCCGQ11LM"
    _name = "Door sensor"
