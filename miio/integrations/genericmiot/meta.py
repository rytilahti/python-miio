import logging
from pathlib import Path
from typing import Optional

import yaml

try:
    from pydantic.v1 import BaseModel
except ImportError:
    from pydantic import BaseModel

from miio.miot_models import MiotBaseModel

_LOGGER = logging.getLogger(__name__)


class MetaBase(BaseModel):
    """Base metadata with description."""

    description: str

    class Config:
        extra = "forbid"


class ActionMeta(MetaBase):
    """Metadata for actions."""


class PropertyMeta(MetaBase):
    """Metadata for properties."""


class ServiceMeta(MetaBase):
    """Metadata for a service, containing per-action and per-property metadata."""

    action: dict[str, ActionMeta] | None = None
    property: dict[str, PropertyMeta] | None = None
    event: dict | None = None

    class Config:
        extra = "forbid"


class Namespace(MetaBase):
    """A namespace (e.g. miot-spec-v2) containing service definitions."""

    fallback: Optional["Namespace"] = None
    services: dict[str, ServiceMeta] | None = None


class Metadata(BaseModel):
    """Loads and provides access to YAML metadata for genericmiot entities.

    Metadata provides human-readable descriptions that override the often-Chinese
    or generic defaults from miotspec files.
    """

    namespaces: dict[str, Namespace]

    @classmethod
    def load(cls, file: Path | None = None) -> "Metadata":
        """Load metadata from the default base.yaml or a custom file."""
        if file is None:
            file = Path(__file__).resolve().parent / "metadata" / "base.yaml"

        _LOGGER.debug("Loading metadata from %s", file)
        with file.open() as f:
            data = yaml.safe_load(f)

        for ns_name, ns_value in data["namespaces"].items():
            if isinstance(ns_value, str):
                ns_path = file.parent / ns_value
                _LOGGER.debug("Loading namespace %s from %s", ns_name, ns_path)
                with ns_path.open() as f:
                    data["namespaces"][ns_name] = yaml.safe_load(f)

        return cls(**data)

    def get_metadata(self, entity: MiotBaseModel) -> dict[str, str] | None:
        """Look up metadata for a miot entity (property or action).

        Returns a dict with a description key, or None if no metadata was found.
        """
        urn = entity.extras.get("urn")
        if urn is None:
            return None

        if entity.service is None:
            return None

        ns_name: str = urn.namespace
        service_name: str = entity.service.name
        type_: str = urn.type
        entity_name: str = urn.name
        full_name = f"{ns_name}:{service_name}:{type_}:{entity_name}"

        ns = self.namespaces.get(ns_name)
        if ns is None:
            _LOGGER.debug("No metadata namespace: %s", ns_name)
            return None

        if ns.services is None:
            return None

        serv = ns.services.get(service_name)
        if serv is None:
            _LOGGER.debug("No metadata for service: %s", service_name)
            return None

        type_dict: dict | None = getattr(serv, type_, None)
        if type_dict is None:
            _LOGGER.debug("No metadata type %s in service %s", type_, service_name)
            return None

        meta: MetaBase | None = type_dict.get(entity_name)
        if meta is None:
            _LOGGER.debug("No metadata for %s", full_name)
            return None

        result: dict[str, str] = {}
        if meta.description:
            result["description"] = meta.description

        _LOGGER.debug("Found metadata for %s: %s", full_name, result)
        return result
