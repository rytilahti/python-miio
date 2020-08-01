"""Xiaomi Zigbee motion."""

from .sub_device import SubDevice


class Motion(SubDevice):
    """Subdevice Motion specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.sensor_motion"
    _model = "RTCGQ01LM"
    _name = "Motion sensor"


class AqaraMotion(SubDevice):
    """Subdevice AqaraMotion specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.sensor_motion.aq2"
    _model = "RTCGQ11LM"
    _name = "Motion sensor"
