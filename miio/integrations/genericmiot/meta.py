import logging
import os
from pathlib import Path
from typing import Dict, Optional

import yaml
from pydantic import BaseModel

_LOGGER = logging.getLogger(__name__)


class Loader(yaml.SafeLoader):
    """Loader to implement !include command.

    From https://stackoverflow.com/a/9577670
    """

    def __init__(self, stream):
        self._root = os.path.split(stream.name)[0]
        super().__init__(stream)

    def include(self, node):
        filename = os.path.join(self._root, self.construct_scalar(node))

        with open(filename) as f:
            return yaml.load(f, Loader)  # nosec


Loader.add_constructor("!include", Loader.include)


class MetaBase(BaseModel):
    """Base class for metadata definitions."""

    description: str
    icon: Optional[str] = None
    device_class: Optional[str] = None  # homeassistant only

    class Config:
        extra = "forbid"


class ActionMeta(MetaBase):
    """Metadata for actions."""


class PropertyMeta(MetaBase):
    """Metadata for properties."""


class ServiceMeta(MetaBase):
    """Describes a service."""

    action: Optional[Dict[str, ActionMeta]]
    property: Optional[Dict[str, PropertyMeta]]
    event: Optional[Dict]

    class Config:
        extra = "forbid"


class Namespace(MetaBase):
    fallback: Optional["Namespace"] = None  # fallback
    services: Optional[Dict[str, ServiceMeta]]


class Metadata(BaseModel):
    namespaces: Dict[str, Namespace]

    @classmethod
    def load(cls, file: Path = None):
        if file is None:
            datadir = Path(__file__).resolve().parent
            file = datadir / "metadata" / "extras.yaml"

        _LOGGER.debug("Loading metadata file %s", file)
        data = yaml.load(file.open(), Loader)  # nosec
        definitions = cls(**data)

        return definitions

    def get_metadata(self, desc):
        extras = {}
        urn = desc.extras["urn"]
        ns_name = urn.namespace
        service = desc.service.name
        type_ = urn.type
        ns = self.namespaces.get(ns_name)
        full_name = f"{ns_name}:{service}:{type_}:{urn.name}"
        _LOGGER.debug("Looking metadata for %s", full_name)
        if ns is not None:
            serv = ns.services.get(service)
            if serv is None:
                _LOGGER.warning("Unable to find service: %s", service)
                return extras

            type_dict = getattr(serv, urn.type, None)
            if type_dict is None:
                _LOGGER.warning(
                    "Unable to find type for service %s: %s", service, urn.type
                )
                return extras

            # TODO: implement fallback to parent?
            extras = type_dict.get(urn.name)
            if extras is None:
                _LOGGER.warning(
                    "Unable to find extras for %s (%s)", urn.name, full_name
                )
            else:
                if extras.icon is None:
                    _LOGGER.warning("Icon missing for %s", full_name)
                if extras.description is None:
                    _LOGGER.warning("Description missing for %s", full_name)
        else:
            _LOGGER.warning("Namespace not found: %s", ns_name)
            # TODO: implement fallback?

        return extras
