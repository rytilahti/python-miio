"""Xiaomi Zigbee various sensors."""

from .sub_device import SubDevice


class SensorSmoke(SubDevice):
    """Subdevice SensorSmoke specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.sensor_smoke"
    _model = "JTYJ-GD-01LM/BW"
    _name = "Honeywell smoke detector"


class SensorNatgas(SubDevice):
    """Subdevice SensorNatgas specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.sensor_natgas"
    _model = "JTQJ-BF-01LM/BW"
    _name = "Honeywell natural gas detector"


class AqaraWaterLeak(SubDevice):
    """Subdevice AqaraWaterLeak specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.sensor_wleak.aq1"
    _model = "SJCGQ11LM"
    _name = "Water leak sensor"


class AqaraVibration(SubDevice):
    """Subdevice AqaraVibration specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.vibration.aq1"
    _model = "DJT11LM"
    _name = "Vibration sensor"
