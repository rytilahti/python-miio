"""Xiaomi Zigbee thermostats."""

from .subdevice import SubDevice


class ThermostatS2(SubDevice):
    """Subdevice ThermostatS2 specific properties and methods."""

    properties = []
    _zigbee_model = "lumi.airrtc.tcpecn02"
    _model = "KTWKQ03ES"
    _name = "Thermostat S2"
