"""Xiaomi Gateway implementation using Miio protecol."""

import logging
import os
import sys
from typing import Dict

import click
import yaml

from ..click_common import command
from ..device import Device
from ..exceptions import DeviceError, DeviceException
from .alarm import Alarm
from .light import Light
from .radio import Radio
from .zigbee import Zigbee

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


from .devices import SubDevice, SubDeviceInfo  # noqa: E402 isort:skip


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
    * get_lumi_bind ["scene", <page number>] for rooms/devices
    """

    def __init__(
        self,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
    ) -> None:
        super().__init__(ip, token, start_id, debug, lazy_discover)

        self._alarm = Alarm(parent=self)
        self._radio = Radio(parent=self)
        self._zigbee = Zigbee(parent=self)
        self._light = Light(parent=self)
        self._devices: Dict[str, SubDevice] = {}
        self._info = None
        self._subdevice_model_map = None
        self._did = None

    def _get_unknown_model(self):
        for model_info in self.subdevice_model_map:
            if model_info.get("type_id") == -1:
                return model_info

    @property
    def alarm(self) -> Alarm:
        """Return alarm control interface."""
        # example: gateway.alarm.on()
        return self._alarm

    @property
    def radio(self) -> Radio:
        """Return radio control interface."""
        return self._radio

    @property
    def zigbee(self) -> Zigbee:
        """Return zigbee control interface."""
        return self._zigbee

    @property
    def light(self) -> Light:
        """Return light control interface."""
        return self._light

    @property
    def devices(self):
        """Return a dict of the already discovered devices."""
        return self._devices

    @property
    def mac(self):
        """Return the mac address of the gateway."""
        if self._info is None:
            self._info = self.info()
        return self._info.mac_address

    @property
    def model(self):
        """Return the zigbee model of the gateway."""
        if self._info is None:
            self._info = self.info()
        return self._info.model

    @property
    def subdevice_model_map(self):
        """Return the subdevice model map."""
        if self._subdevice_model_map is None:
            subdevice_file = os.path.dirname(__file__) + "/devices/subdevices.yaml"
            with open(subdevice_file) as filedata:
                self._subdevice_model_map = yaml.safe_load(filedata)
        return self._subdevice_model_map

    @command()
    def discover_devices(self):
        """Discovers SubDevices and returns a list of the discovered devices."""

        self._devices = {}

        # Skip the models which do not support getting the device list
        if self.model == GATEWAY_MODEL_EU:
            _LOGGER.warning(
                "Gateway model '%s' does not (yet) support getting the device list, "
                "try using the get_devices_from_dict function with micloud",
                self.model,
            )
            return self._devices

        if self.model == GATEWAY_MODEL_ZIG3:
            # self.get_prop("device_list") does not work for the GATEWAY_MODEL_ZIG3
            # self.send("get_device_list") does work for the GATEWAY_MODEL_ZIG3 but gives slightly diffrent return values
            devices_raw = self.send("get_device_list")

            if type(devices_raw) != list:
                _LOGGER.debug(
                    "Gateway response to 'get_device_list' not a list type, no zigbee devices connected."
                )
                return self._devices

            for device in devices_raw:
                # Match 'model' to get the model_info
                model_info = self.match_zigbee_model(device["model"], device["did"])

                # Extract discovered information
                dev_info = SubDeviceInfo(
                    device["did"], model_info["type_id"], -1, -1, -1
                )

                # Setup the device
                self.setup_device(dev_info, model_info)
        else:
            devices_raw = self.get_prop("device_list")

            for x in range(0, len(devices_raw), 5):
                # Extract discovered information
                dev_info = SubDeviceInfo(*devices_raw[x : x + 5])

                # Match 'type_id' to get the model_info
                model_info = self.match_type_id(dev_info.type_id, dev_info.sid)

                # Setup the device
                self.setup_device(dev_info, model_info)

        return self._devices

    @command()
    def get_devices_from_dict(self, device_dict):
        """Get SubDevices from a dict containing at least "mac", "did", "parent_id" and
        "model".

        This dict can be obtained with the micloud package:
        https://github.com/squachen/micloud
        """

        self._devices = {}

        # find the gateway
        for device in device_dict:
            if device["mac"] == self.mac:
                self._did = device["did"]
                break

        # check if the gateway is found
        if self._did is None:
            _LOGGER.error(
                "Could not find gateway with ip '%s', mac '%s', model '%s' in the cloud device list response",
                self.ip,
                self.mac,
                self.model,
            )
            return self._devices

        # find the subdevices belonging to this gateway
        for device in device_dict:
            if device.get("parent_id") == self._did:
                # Match 'model' to get the type_id
                model_info = self.match_zigbee_model(device["model"], device["did"])

                # Extract discovered information
                dev_info = SubDeviceInfo(
                    device["did"], model_info["type_id"], -1, -1, -1
                )

                # Setup the device
                self.setup_device(dev_info, model_info)

        return self._devices

    @command(click.argument("zigbee_model", "sid"))
    def match_zigbee_model(self, zigbee_model, sid):
        """Match the zigbee_model to obtain the model_info."""

        for model_info in self.subdevice_model_map:
            if model_info.get("zigbee_id") == zigbee_model:
                return model_info

        _LOGGER.warning(
            "Unknown subdevice discovered, could not match zigbee_model '%s' "
            "of subdevice sid '%s' from Xiaomi gateway with ip: %s",
            zigbee_model,
            sid,
            self.ip,
        )
        return self._get_unknown_model()

    @command(click.argument("type_id", "sid"))
    def match_type_id(self, type_id, sid):
        """Match the type_id to obtain the model_info."""

        for model_info in self.subdevice_model_map:
            if model_info.get("type_id") == type_id:
                return model_info

        _LOGGER.warning(
            "Unknown subdevice discovered, could not match type_id '%i' "
            "of subdevice sid '%s' from Xiaomi gateway with ip: %s",
            type_id,
            sid,
            self.ip,
        )
        return self._get_unknown_model()

    @command(click.argument("dev_info", "model_info"))
    def setup_device(self, dev_info, model_info):
        """Setup a device using the SubDeviceInfo and model_info."""

        if model_info.get("type") == "Gateway":
            # ignore the gateway itself
            return

        # Obtain the correct subdevice class
        subdevice_cls = getattr(
            sys.modules["miio.gateway.devices"], model_info.get("class")
        )
        if subdevice_cls is None:
            subdevice_cls = SubDevice
            _LOGGER.info(
                "Gateway device type '%s' "
                "does not have device specific methods defined, "
                "only basic default methods will be available",
                model_info.get("type"),
            )

        # Initialize and save the subdevice
        self._devices[dev_info.sid] = subdevice_cls(self, dev_info, model_info)
        if self._devices[dev_info.sid].status == {}:
            _LOGGER.info(
                "Discovered subdevice type '%s', has no device specific properties defined, "
                "this device has not been fully implemented yet (model: %s, name: %s).",
                model_info.get("type"),
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
        """Alarm clock."""
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
        """Enable root telnet acces to the operating system, use login "admin" or "app",
        no password."""
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
        """Get illumination.

        In lux?
        """
        try:
            return self.send("get_illumination").pop()
        except Exception as ex:
            raise GatewayException(
                "Got an exception while getting gateway illumination"
            ) from ex
