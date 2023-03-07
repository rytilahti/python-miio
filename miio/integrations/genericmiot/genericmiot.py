import logging
from functools import partial
from typing import Dict, List, Optional

import click

from miio import DeviceInfo, MiotDevice
from miio.click_common import LiteralParamType, command, format_output
from miio.descriptors import AccessFlags, ActionDescriptor, PropertyDescriptor
from miio.miot_cloud import MiotCloud
from miio.miot_device import MiotMapping
from miio.miot_models import (
    DeviceModel,
    MiotAccess,
    MiotAction,
    MiotProperty,
    MiotService,
)

from .cli_helpers import pretty_actions, pretty_properties
from .status import GenericMiotStatus

_LOGGER = logging.getLogger(__name__)


class GenericMiot(MiotDevice):
    # we support all devices, if not, it is a responsibility of caller to verify that
    _supported_models = ["*"]

    def __init__(
        self,
        ip: Optional[str] = None,
        token: Optional[str] = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
        timeout: Optional[int] = None,
        *,
        model: Optional[str] = None,
        mapping: Optional[MiotMapping] = None,
    ):
        super().__init__(
            ip,
            token,
            start_id,
            debug,
            lazy_discover,
            timeout,
            model=model,
            mapping=mapping,
        )
        self._model = model
        self._miot_model: Optional[DeviceModel] = None

        self._actions: Dict[str, ActionDescriptor] = {}
        self._properties: Dict[str, PropertyDescriptor] = {}
        self._all_properties: List[MiotProperty] = []

    def initialize_model(self):
        """Initialize the miot model and create descriptions."""
        if self._miot_model is not None:
            return

        miotcloud = MiotCloud()
        self._miot_model = miotcloud.get_device_model(self.model)
        _LOGGER.debug("Initialized: %s", self._miot_model)
        self._create_descriptors()

    @command()
    def status(self) -> GenericMiotStatus:
        """Return status based on the miot model."""
        properties = []
        for prop in self._all_properties:
            if MiotAccess.Read not in prop.access:
                continue

            name = prop.name
            q = {"siid": prop.siid, "piid": prop.piid, "did": name}
            properties.append(q)

        # TODO: max properties needs to be made configurable (or at least splitted to avoid too large udp datagrams
        #       some devices are stricter: https://github.com/rytilahti/python-miio/issues/1550#issuecomment-1303046286
        response = self.get_properties(
            properties, property_getter="get_properties", max_properties=10
        )

        return GenericMiotStatus(response, self)

    def _create_action(self, act: MiotAction) -> Optional[ActionDescriptor]:
        """Create action descriptor for miot action."""
        desc = act.get_descriptor()
        if not desc:
            return None

        call_action = partial(self.call_action_by, act.siid, act.aiid)
        desc.method = call_action

        return desc

    def _create_actions(self, serv: MiotService):
        """Create action descriptors."""
        for act in serv.actions:
            act_desc = self._create_action(act)
            if act_desc is None:  # skip actions we cannot handle for now..
                continue

            if (
                act_desc.name in self._actions
            ):  # TODO: find a way to handle duplicates, suffix maybe?
                _LOGGER.warning("Got used name name, ignoring '%s': %s", act.name, act)
                continue

            self._actions[act_desc.name] = act_desc

    def _create_properties(self, serv: MiotService):
        """Create sensor and setting descriptors for a service."""
        for prop in serv.properties:
            if prop.access == [MiotAccess.Notify]:
                _LOGGER.debug("Skipping notify-only property: %s", prop)
                continue
            if not prop.access:
                # some properties are defined only to be used as inputs or outputs for actions
                _LOGGER.debug(
                    "%s (%s) reported no access information",
                    prop.name,
                    prop.description,
                )
                continue

            desc = prop.get_descriptor()

            if desc.access & AccessFlags.Write:
                desc.setter = partial(
                    self.set_property_by, prop.siid, prop.piid, name=prop.name
                )

            self._properties[prop.name] = desc
            # TODO: all properties is only used as the descriptors (stored in _properties) do not have siid/piid
            self._all_properties.append(prop)

    def _create_descriptors(self):
        """Create descriptors based on the miot model."""
        for serv in self._miot_model.services:
            if serv.siid == 1:
                continue  # Skip device details

            self._create_actions(serv)
            self._create_properties(serv)

        _LOGGER.debug("Created %s actions", len(self._actions))
        for act in self._actions.values():
            _LOGGER.debug(f"\t{act}")
        _LOGGER.debug("Created %s properties", len(self._properties))
        for sensor in self._properties.values():
            _LOGGER.debug(f"\t{sensor}")

    def _get_action_by_name(self, name: str):
        """Return action by name."""
        # TODO: cache service:action?
        for act in self._actions.values():
            if act.id == name:
                if act.method_name is not None:
                    act.method = getattr(self, act.method_name)

                return act

        raise ValueError("No action with name/id %s" % name)

    @command(
        click.argument("name"),
        click.argument("params", type=LiteralParamType(), required=False),
        name="call",
    )
    def call_action(self, name: str, params=None):
        """Call action by name."""
        params = params or []
        act = self._get_action_by_name(name)
        return act.method(params)

    @command(
        click.argument("name"),
        click.argument("params", type=LiteralParamType(), required=True),
        name="set",
    )
    def change_setting(self, name: str, params=None):
        """Change setting value."""
        params = params if params is not None else []
        setting = self._properties.get(name, None)
        if setting is None:
            raise ValueError("No property found for name %s" % name)
        if setting.access & AccessFlags.Write == 0:
            raise ValueError("Property %s is not writable" % name)

        return setting.setter(value=params)

    def _fetch_info(self) -> DeviceInfo:
        """Hook to perform the model initialization."""
        info = super()._fetch_info()
        self.initialize_model()

        return info

    @command(default_output=format_output(result_msg_fmt=pretty_actions))
    def actions(self) -> Dict[str, ActionDescriptor]:
        """Return available actions."""
        return self._actions

    @command(default_output=format_output(result_msg_fmt=pretty_properties))
    def properties(self) -> Dict[str, PropertyDescriptor]:
        """Return available sensors."""
        # TODO: move pretty-properties to be generic for all devices
        return self._properties

    @property
    def device_type(self) -> Optional[str]:
        """Return device type."""
        # TODO: this should be probably mapped to an enum
        if self._miot_model is not None:
            return self._miot_model.urn.type
        return None

    @classmethod
    def get_device_group(cls):
        """Return device command group.

        TODO: insert the actions from the model for better click integration
        """
        return super().get_device_group()
