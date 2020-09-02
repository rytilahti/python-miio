"""Xiaomi Gateway implementation using Miio protecol."""

import logging

import click

from ..click_common import command
from ..device import Device
from ..exceptions import DeviceError, DeviceException

_LOGGER = logging.getLogger(__name__)

GATEWAY_MODEL_CHINA = "lumi.gateway.v3"
GATEWAY_MODEL_EU = "lumi.gateway.mieu01"
GATEWAY_MODEL_ZIG3 = "lumi.gateway.mgl03"
GATEWAY_MODEL_AQARA = "lumi.gateway.aqhm01"
GATEWAY_MODEL_AC_V1 = "lumi.acpartner.v1"
GATEWAY_MODEL_AC_V2 = "lumi.acpartner.v2"
GATEWAY_MODEL_AC_V3 = "lumi.acpartner.v3"


class GatewayException(DeviceException):
    """Exception for the Xioami Gateway communication."""


class Gateway(Device):
    """Main class representing the Xiaomi Gateway.

    Use the given property getters to access specific functionalities such
    as `alarm` (for alarm controls) or `light` (for lights).

    Commands whose functionality or parameters are unknown,
    feel free to implement!
    * toggle_device
    * toggle_plug
    * remove_all_bind
    * list_bind [0]
    * bind_page
    * bind
    * remove_bind

    * self.get_prop("used_for_public") # Return the 'used_for_public' status, return value: [0] or [1], probably this has to do with developer mode.
    * self.set_prop("used_for_public", state) # Set the 'used_for_public' state, value: 0 or 1, probably this has to do with developer mode.

    * welcome
    * set_curtain_level

    * get_corridor_on_time
    * set_corridor_light ["off"]
    * get_corridor_light -> "on"

    * set_default_sound
    * set_doorbell_push, get_doorbell_push ["off"]
    * set_doorbell_volume [100], get_doorbell_volume
    * set_gateway_volume, get_gateway_volume
    * set_clock_volume
    * set_clock
    * get_sys_data
    * update_neighbor_token [{"did":x, "token":x, "ip":x}]

    ## property getters
    * ctrl_device_prop
    * get_device_prop_exp [[sid, list, of, properties]]

    ## scene
    * get_lumi_bind ["scene", <page number>] for rooms/devices"""

    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
    ) -> None:
        super().__init__(ip, token, start_id, debug, lazy_discover)

        from . import (
            Alarm,
            Radio,
            Zigbee,
            Light,
        )

        self._alarm = Alarm(parent=self)
        self._radio = Radio(parent=self)
        self._zigbee = Zigbee(parent=self)
        self._light = Light(parent=self)
        self._devices = {}
        self._info = None

    @property
    def alarm(self) -> "GatewayAlarm":  # noqa: F821
        """Return alarm control interface."""
        # example: gateway.alarm.on()
        return self._alarm

    @property
    def radio(self) -> "GatewayRadio":  # noqa: F821
        """Return radio control interface."""
        return self._radio

    @property
    def zigbee(self) -> "GatewayZigbee":  # noqa: F821
        """Return zigbee control interface."""
        return self._zigbee

    @property
    def light(self) -> "GatewayLight":  # noqa: F821
        """Return light control interface."""
        return self._light

    @property
    def devices(self):
        """Return a dict of the already discovered devices."""
        return self._devices

    @property
    def model(self):
        """Return the zigbee model of the gateway."""
        # Check if catch already has the gateway info, otherwise get it from the device
        if self._info is None:
            self._info = self.info()
        return self._info.model

    @command()
    def discover_devices(self):
        """
        Discovers SubDevices
        and returns a list of the discovered devices.
        """

        from .devices import DeviceType, DeviceTypeMapping, SubDevice, SubDeviceInfo

        self._devices = {}

        # Skip the models which do not support getting the device list
        if self.model == GATEWAY_MODEL_EU:
            _LOGGER.warning(
                "Gateway model '%s' does not (yet) support getting the device list",
                self.model,
            )
            return self._devices

        if self.model == GATEWAY_MODEL_ZIG3:
            # self.get_prop("device_list") does not work for the GATEWAY_MODEL_ZIG3
            # self.send("get_device_list") does work for the GATEWAY_MODEL_ZIG3 but gives slightly diffrent return values
            devices_raw = self.send("get_device_list")

            for device in devices_raw:
                # Match 'model' to get the type_id
                type_id = self.match_zigbee_model(device["model"])

                # Extract discovered information
                dev_info = SubDeviceInfo(device["did"], type_id, -1, -1, -1)

                # Setup the device
                self.setup_device(dev_info)
        else:
            devices_raw = self.get_prop("device_list")

            for x in range(0, len(devices_raw), 5):
                # Extract discovered information
                dev_info = SubDeviceInfo(*devices_raw[x : x + 5])

                # Setup the device
                self.setup_device(dev_info)

        return self._devices

    @command(click.argument("zigbee_model"))
    def match_zigbee_model(self, zigbee_model):
        """
        Match the zigbee_model to obtain the type_id
        """

        from .devices import DeviceType, DeviceTypeMapping

        for type_id in DeviceTypeMapping:
            if DeviceTypeMapping[type_id]._zigbee_model == zigbee_model:
                return type_id

        _LOGGER.warning(
            "Unknown subdevice discovered, could not match zigbee_model '%s' "
            "of Xiaomi gateway with ip: %s",
            zigbee_model,
            self.ip,
        )
        return DeviceType.Unknown

    @command(click.argument("dev_info"))
    def setup_device(self, dev_info):
        """
        Setup a device using the SubDeviceInfo
        """

        from .devices import DeviceType, DeviceTypeMapping, SubDevice

        # Construct DeviceType
        try:
            device_type = DeviceType(dev_info.type_id)
        except ValueError:
            _LOGGER.warning(
                "Unknown subdevice type %s discovered, "
                "of Xiaomi gateway with ip: %s",
                dev_info,
                self.ip,
            )
            device_type = DeviceType(-1)

        # Obtain the correct subdevice class, ignoring the gateway itself
        subdevice_cls = DeviceTypeMapping.get(device_type)
        if subdevice_cls is None and device_type != DeviceType.Gateway:
            subdevice_cls = SubDevice
            _LOGGER.info(
                "Gateway device type '%s' "
                "does not have device specific methods defined, "
                "only basic default methods will be available",
                device_type.name,
            )

        # Initialize and save the subdevice, ignoring the gateway itself
        if device_type != DeviceType.Gateway:
            self._devices[dev_info.sid] = subdevice_cls(self, dev_info)
            if self._devices[dev_info.sid].status == {}:
                _LOGGER.info(
                    "Discovered subdevice type '%s', has no device specific properties defined, "
                    "this device has not been fully implemented yet (model: %s, name: %s).",
                    device_type.name,
                    self._devices[dev_info.sid].model,
                    self._devices[dev_info.sid].name,
                )

        return self._devices[dev_info.sid]

    @command(click.argument("property"))
    def get_prop(self, property):
        """Get the value of a property for given sid."""
        return self.send("get_device_prop", ["lumi.0", property])

    @command(click.argument("properties", nargs=-1))
    def get_prop_exp(self, properties):
        """Get the value of a bunch of properties for given sid."""
        return self.send("get_device_prop_exp", [["lumi.0"] + list(properties)])

    @command(click.argument("property"), click.argument("value"))
    def set_prop(self, property, value):
        """Set the device property."""
        return self.send("set_device_prop", {"sid": "lumi.0", property: value})

    @command()
    def clock(self):
        """Alarm clock"""
        # payload of clock volume ("get_clock_volume")
        # already in get_clock response
        return self.send("get_clock")

    # Developer key
    @command()
    def get_developer_key(self):
        """Return the developer API key."""
        return self.send("get_lumi_dpf_aes_key")[0]

    @command(click.argument("key"))
    def set_developer_key(self, key):
        """Set the developer API key."""
        if len(key) != 16:
            click.echo("Key must be of length 16, was %s" % len(key))

        return self.send("set_lumi_dpf_aes_key", [key])

    @command()
    def enable_telnet(self):
        """Enable root telnet acces to the operating system, use login "admin" or "app", no password."""
        try:
            return self.send("enable_telnet_service")
        except DeviceError:
            _LOGGER.error(
                "Gateway model '%s' does not (yet) support enabling the telnet interface",
                self.model,
            )
            return None

    @command()
    def timezone(self):
        """Get current timezone."""
        return self.get_prop("tzone_sec")

    @command()
    def get_illumination(self):
        """Get illumination. In lux?"""
        return self.send("get_illumination").pop()
