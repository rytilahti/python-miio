"""Xiaomi Zigbee Cube."""

from .sub_device import SubDevice


class Cube(SubDevice):
    """Subdevice Cube specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.sensor_cube.v1"
    _model = "MFKZQ01LM"
    _name = "Cube"


class CubeV2(SubDevice):
    """Subdevice CubeV2 specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.sensor_cube.aqgl01"
    _model = "MFKZQ01LM"
    _name = "Cube"
