import logging
from functools import partial
from typing import Dict, Iterable, List, Optional, cast

import click

from miio import DeviceInfo, DeviceStatus, MiotDevice
from miio.click_common import LiteralParamType, command, format_output
from miio.descriptors import ActionDescriptor, SensorDescriptor, SettingDescriptor
from miio.miot_cloud import MiotCloud
from miio.miot_device import MiotMapping
from miio.miot_models import (
    DeviceModel,
    MiotAccess,
    MiotAction,
    MiotProperty,
    MiotService,
)

_LOGGER = logging.getLogger(__name__)


def pretty_actions(result: Dict[str, ActionDescriptor]):
    """Pretty print actions."""
    out = ""
    service = None
    for _, desc in result.items():
        miot_prop: MiotProperty = desc.extras["miot_action"]
        # service is marked as optional due pydantic backrefs..
        serv = cast(MiotService, miot_prop.service)
        if service is None or service.siid != serv.siid:
            service = serv
            out += f"[bold]{service.description} ({service.name})[/bold]\n"

        out += f"\t{desc.id}\t\t{desc.name}"
        if desc.inputs:
            for idx, input_ in enumerate(desc.inputs, start=1):
                param = input_.extras[
                    "miot_property"
                ]  # TODO: hack until descriptors get support for descriptions
                param_desc = f"\n\t\tParameter #{idx}: {param.name} ({param.description}) ({param.format}) {param.pretty_input_constraints}"
                out += param_desc

        out += "\n"

    return out


def pretty_settings(result: Dict[str, SettingDescriptor]):
    """Pretty print settings."""
    out = ""
    verbose = False
    service = None
    for _, desc in result.items():
        miot_prop: MiotProperty = desc.extras["miot_property"]
        # service is marked as optional due pydantic backrefs..
        serv = cast(MiotService, miot_prop.service)
        if service is None or service.siid != serv.siid:
            service = serv
            out += f"[bold]{service.name}[/bold] ({service.description})\n"

        out += f"\t{desc.name} ({desc.id}, access: {miot_prop.pretty_access})\n"
        if verbose:
            out += f'  urn: {repr(desc.extras["urn"])}\n'
            out += f'  siid: {desc.extras["siid"]}\n'
            out += f'  piid: {desc.extras["piid"]}\n'

    return out


class GenericMiotStatus(DeviceStatus):
    """Generic status for miot devices."""

    def __init__(self, response, dev):
        self._model: DeviceModel = dev._miot_model
        self._dev = dev
        self._data = {elem["did"]: elem["value"] for elem in response}
        # for hardcoded json output.. see click_common.json_output
        self.data = self._data

        self._data_by_siid_piid = {
            (elem["siid"], elem["piid"]): elem["value"] for elem in response
        }
        self._data_by_normalized_name = {
            self._normalize_name(elem["did"]): elem["value"] for elem in response
        }

    def _normalize_name(self, id_: str) -> str:
        """Return a cleaned id for dict searches."""
        return id_.replace(":", "_").replace("-", "_")

    def __getattr__(self, item):
        """Return attribute for name.

        This is overridden to provide access to properties using (siid, piid) tuple.
        """
        # let devicestatus handle dunder methods
        if item.startswith("__") and item.endswith("__"):
            return super().__getattr__(item)

        normalized_name = self._normalize_name(item)
        if normalized_name in self._data_by_normalized_name:
            return self._data_by_normalized_name[normalized_name]

        # TODO: create a helper method and prohibit using non-normalized names
        if ":" in item:
            _LOGGER.warning("Use normalized names for accessing properties")
            serv, prop = item.split(":")
            prop = self._model.get_property(serv, prop)
            value = self._data[item]

            # TODO: this feels like a wrong place to convert value to enum..
            if prop.choices is not None:
                for choice in prop.choices:
                    if choice.value == value:
                        return choice.description

                _LOGGER.warning(
                    "Unable to find choice for value: %s: %s", value, prop.choices
                )

        return self._data[item]

    @property
    def device(self) -> "GenericMiot":
        """Return the device which returned this status."""
        return self._dev

    def property_dict(self) -> Dict[str, MiotProperty]:
        """Return name-keyed dictionary of properties."""
        res = {}

        # We use (siid, piid) to locate the property as not all devices mirror the did in response
        for (siid, piid), value in self._data_by_siid_piid.items():
            prop = self._model.get_property_by_siid_piid(siid, piid)
            prop.value = value
            res[prop.name] = prop

        return res

    @property
    def __cli_output__(self):
        """Return a CLI printable status."""
        out = ""
        props = self.property_dict()
        service = None
        for _name, prop in props.items():
            miot_prop: MiotProperty = prop.extras["miot_property"]
            if service is None or miot_prop.siid != service.siid:
                service = miot_prop.service
                out += f"Service [bold]{service.description} ({service.name})[/bold]\n"  # type: ignore  # FIXME

            out += f"\t{prop.description} ({prop.name}, access: {prop.pretty_access}): {prop.pretty_value}"

            if MiotAccess.Write in miot_prop.access:
                out += f" ({prop.format}"
                if prop.pretty_input_constraints is not None:
                    out += f", {prop.pretty_input_constraints}"
                out += ")"

            if self.device._debug > 1:
                out += "\n\t[bold]Extras[/bold]\n"
                for extra_key, extra_value in prop.extras.items():
                    out += f"\t\t{extra_key} = {extra_value}\n"

            out += "\n"

        return out

    def __dir__(self) -> Iterable[str]:
        """Return a list of properties."""
        return list(super().__dir__()) + list(self._data_by_normalized_name.keys())

    def __repr__(self):
        s = f"<{self.__class__.__name__}"
        for name, value in self.property_dict().items():
            s += f" {name}={value}"
        s += ">"

        return s


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
        self._sensors: Dict[str, SensorDescriptor] = {}
        self._settings: Dict[str, SettingDescriptor] = {}
        self._properties: List[MiotProperty] = []

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
        for prop in self._properties:
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

    def _create_sensors_and_settings(self, serv: MiotService):
        """Create sensor and setting descriptors for a service."""
        for prop in serv.properties:
            if prop.access == [MiotAccess.Notify]:
                _LOGGER.debug("Skipping notify-only property: %s", prop)
                continue
            if not prop.access:
                # some properties are defined only to be used as inputs for actions
                _LOGGER.debug(
                    "%s (%s) reported no access information",
                    prop.name,
                    prop.description,
                )
                continue

            desc = prop.get_descriptor()

            if isinstance(desc, SensorDescriptor):
                self._sensors[prop.name] = desc
            elif isinstance(desc, SettingDescriptor):
                desc.setter = partial(
                    self.set_property_by, prop.siid, prop.piid, name=prop.name
                )
                self._settings[prop.name] = desc
            else:
                raise Exception("unknown descriptor type")

            self._properties.append(prop)

    def _create_descriptors(self):
        """Create descriptors based on the miot model."""
        for serv in self._miot_model.services:
            if serv.siid == 1:
                continue  # Skip device details

            self._create_actions(serv)
            self._create_sensors_and_settings(serv)

        _LOGGER.debug("Created %s actions", len(self._actions))
        for act in self._actions.values():
            _LOGGER.debug(f"\t{act}")
        _LOGGER.debug("Created %s sensors", len(self._sensors))
        for sensor in self._sensors.values():
            _LOGGER.debug(f"\t{sensor}")
        _LOGGER.debug("Created %s settings", len(self._settings))
        for setting in self._settings.values():
            _LOGGER.debug(f"\t{setting}")

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
        setting = self._settings.get(name, None)
        if setting is None:
            raise ValueError("No setting found for name %s" % name)

        return setting.setter(value=setting.cast_value(params))

    def _fetch_info(self) -> DeviceInfo:
        """Hook to perform the model initialization."""
        info = super()._fetch_info()
        self.initialize_model()

        return info

    @command(default_output=format_output(result_msg_fmt=pretty_actions))
    def actions(self) -> Dict[str, ActionDescriptor]:
        """Return available actions."""
        return self._actions

    @command()
    def sensors(self) -> Dict[str, SensorDescriptor]:
        """Return available sensors."""
        return self._sensors

    @command(default_output=format_output(result_msg_fmt=pretty_settings))
    def settings(self) -> Dict[str, SettingDescriptor]:
        """Return available settings."""
        return self._settings

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
