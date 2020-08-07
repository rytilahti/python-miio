"""Xiaomi Zigbee Cube."""

from .sub_device import SubDevice


class CubeDevice(SubDevice):
    """Base class for subdevice cube."""

    properties = []


class Cube(CubeDevice):
    """Subdevice Cube specific properties and methods."""

    _zigbee_model = "lumi.sensor_cube.v1"
    _model = "MFKZQ01LM"
    _name = "Cube"


class CubeV2(CubeDevice):
    """Subdevice CubeV2 specific properties and methods."""

    _zigbee_model = "lumi.sensor_cube.aqgl01"
    _model = "MFKZQ01LM"
    _name = "Cube"
