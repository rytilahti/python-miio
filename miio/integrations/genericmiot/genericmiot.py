import logging
from functools import partial
from typing import Dict, Optional

from miio import MiotDevice
from miio.click_common import command
from miio.descriptors import AccessFlags, ActionDescriptor, PropertyDescriptor
from miio.miot_cloud import MiotCloud
from miio.miot_device import MiotMapping
from miio.miot_models import DeviceModel, MiotAccess, MiotAction, MiotService

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
        for _, prop in self.sensors().items():
            extras = prop.extras
            prop = extras["miot_property"]
            q = {"siid": prop.siid, "piid": prop.piid, "did": prop.name}
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
        call_action = partial(self.call_action_by, act.siid, act.aiid)
        desc.method = call_action

        return desc

    def _create_actions(self, serv: MiotService):
        """Create action descriptors."""
        for act in serv.actions:
            act_desc = self._create_action(act)
            self.descriptors().add_descriptor(act_desc)

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

            self.descriptors().add_descriptor(desc)

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

    def _initialize_descriptors(self) -> None:
        """Initialize descriptors.

        This will be called by the base class to initialize the descriptors. We override
        it here to construct our model instead of trying to request  the status and use
        that to find out the available features.
        """
        self.initialize_model()
        self._initialized = True

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
