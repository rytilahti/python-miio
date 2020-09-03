"""Xiaomi Gateway subdevice base class."""

import logging
from typing import Optional

import attr
import click

from ...click_common import command
from ..gateway import GATEWAY_MODEL_EU, Gateway, GatewayException

_LOGGER = logging.getLogger(__name__)


@attr.s(auto_attribs=True)
class SubDeviceInfo:
    """SubDevice discovery info."""

    sid: str
    type_id: int
    unknown: int
    unknown2: int
    fw_ver: int


class SubDevice:
    """
    Base class for all subdevices of the gateway
    these devices are connected through zigbee.
    """

    _zigbee_model = "unknown"
    _model = "unknown"
    _name = "unknown"

    @attr.s(auto_attribs=True)
    class props:
        """Defines properties of the specific device."""

    def __init__(
        self,
        gw: Gateway = None,
        dev_info: SubDeviceInfo = None,
    ) -> None:

        from . import DeviceType

        self._gw = gw
        self.sid = dev_info.sid
        self._battery = None
        self._voltage = None
        self._fw_ver = dev_info.fw_ver
        self._props = self.props()
        try:
            self.type = DeviceType(dev_info.type_id)
        except ValueError:
            self.type = DeviceType.Unknown

    def __repr__(self):
        return "<Subdevice %s: %s, model: %s, zigbee: %s, fw: %s, bat: %s, vol: %s, props: %s>" % (
            self.device_type,
            self.sid,
            self.model,
            self.zigbee_model,
            self.firmware_version,
            self.get_battery(),
            self.get_voltage(),
            self.status,
        )

    @property
    def status(self):
        """Return sub-device status as a dict containing all properties."""
        return attr.asdict(self._props)

    @property
    def device_type(self):
        """Return the device type name."""
        return self.type.name

    @property
    def name(self):
        """Return the name of the device."""
        return f"{self._name} ({self.sid})"

    @property
    def model(self):
        """Return the device model."""
        return self._model

    @property
    def zigbee_model(self):
        """Return the zigbee device model."""
        return self._zigbee_model

    @property
    def firmware_version(self):
        """Return the firmware version."""
        return self._fw_ver

    @property
    def battery(self):
        """Return the battery level in %."""
        return self._battery

    @property
    def voltage(self):
        """Return the battery voltage in V."""
        return self._voltage

    @command()
    def update(self):
        """Update the device-specific properties."""
        _LOGGER.debug(
            "Subdevice '%s' does not have a device specific update method defined",
            self.device_type,
        )

    @command()
    def send(self, command):
        """Send a command/query to the subdevice."""
        try:
            return self._gw.send(command, [self.sid])
        except Exception as ex:
            raise GatewayException(
                "Got an exception while sending command %s" % (command)
            ) from ex

    @command()
    def send_arg(self, command, arguments):
        """Send a command/query including arguments to the subdevice."""
        try:
            return self._gw.send(command, arguments, extra_parameters={"sid": self.sid})
        except Exception as ex:
            raise GatewayException(
                "Got an exception while sending "
                "command '%s' with arguments '%s'" % (command, str(arguments))
            ) from ex

    @command(click.argument("property"))
    def get_property(self, property):
        """Get the value of a property of the subdevice."""
        try:
            response = self._gw.send("get_device_prop", [self.sid, property])
        except Exception as ex:
            raise GatewayException(
                "Got an exception while fetching property %s" % (property)
            ) from ex

        if not response:
            raise GatewayException(
                "Empty response while fetching property '%s': %s" % (property, response)
            )

        return response

    @command(click.argument("properties", nargs=-1))
    def get_property_exp(self, properties):
        """Get the value of a bunch of properties of the subdevice."""
        try:
            response = self._gw.send(
                "get_device_prop_exp", [[self.sid] + list(properties)]
            ).pop()
        except Exception as ex:
            raise GatewayException(
                "Got an exception while fetching properties %s: %s" % (properties)
            ) from ex

        if len(list(properties)) != len(response):
            raise GatewayException(
                "unexpected result while fetching properties %s: %s"
                % (properties, response)
            )

        return response

    @command(click.argument("property"), click.argument("value"))
    def set_property(self, property, value):
        """Set a device property of the subdevice."""
        try:
            return self._gw.send("set_device_prop", {"sid": self.sid, property: value})
        except Exception as ex:
            raise GatewayException(
                "Got an exception while setting propertie %s to value %s"
                % (property, str(value))
            ) from ex

    @command()
    def unpair(self):
        """Unpair this device from the gateway."""
        return self.send("remove_device")

    @command()
    def get_battery(self):
        """Update the battery level, if available."""
        if self._gw.model != GATEWAY_MODEL_EU:
            self._battery = self.send("get_battery").pop()
        else:
            _LOGGER.info(
                "Gateway model '%s' does not (yet) support get_battery",
                self._gw.model,
            )
        return self._battery

    @command()
    def get_voltage(self):
        """Update the battery voltage, if available."""
        if self._gw.model == GATEWAY_MODEL_EU:
            self._voltage = self.get_property("voltage").pop() / 1000
        else:
            _LOGGER.info(
                "Gateway model '%s' does not (yet) support get_voltage",
                self._gw.model,
            )
        return self._voltage

    @command()
    def get_firmware_version(self) -> Optional[int]:
        """Returns firmware version."""
        try:
            self._fw_ver = self.get_property("fw_ver").pop()
        except Exception as ex:
            _LOGGER.info(
                "get_firmware_version failed, returning firmware version from discovery info: %s",
                ex,
            )
        return self._fw_ver
