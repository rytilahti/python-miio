import logging
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

try:
    from pydantic.v1 import BaseModel
except ImportError:
    from pydantic import BaseModel

from miio.miot_models import MiotBaseModel

_LOGGER = logging.getLogger(__name__)


class _IncludeLoader(yaml.SafeLoader):
    """YAML loader that supports !include directives for splitting metadata."""

    def __init__(self, stream: Any) -> None:
        self._root = Path(stream.name).parent
        super().__init__(stream)

    def include(self, node: yaml.Node) -> Any:
        path = self._root / self.construct_scalar(node)
        with path.open() as f:
            return yaml.load(f, _IncludeLoader)


_IncludeLoader.add_constructor("!include", _IncludeLoader.include)


class MetaBase(BaseModel):
    """Base metadata with description, icon, and device_class."""

    description: str
    icon: Optional[str] = None
    device_class: Optional[str] = None

    class Config:
        extra = "forbid"


class ActionMeta(MetaBase):
    """Metadata for actions."""


class PropertyMeta(MetaBase):
    """Metadata for properties."""


class ServiceMeta(MetaBase):
    """Metadata for a service, containing per-action and per-property metadata."""

    action: Optional[Dict[str, ActionMeta]] = None
    property: Optional[Dict[str, PropertyMeta]] = None
    event: Optional[Dict] = None

    class Config:
        extra = "forbid"


class Namespace(MetaBase):
    """A namespace (e.g. miot-spec-v2) containing service definitions."""

    fallback: Optional["Namespace"] = None
    services: Optional[Dict[str, ServiceMeta]] = None


class Metadata(BaseModel):
    """Loads and provides access to YAML metadata for genericmiot entities.

    Metadata provides human-readable descriptions, icons, and device_class
    attributes that override the often-Chinese or generic defaults from miotspec
    files.
    """

    namespaces: Dict[str, Namespace]

    @classmethod
    def load(cls, file: Optional[Path] = None) -> "Metadata":
        """Load metadata from the default extras.yaml or a custom file."""
        if file is None:
            file = Path(__file__).resolve().parent / "metadata" / "extras.yaml"

        _LOGGER.debug("Loading metadata from %s", file)
        with file.open() as f:
            data = yaml.load(f, _IncludeLoader)
        return cls(**data)

    def get_metadata(self, entity: MiotBaseModel) -> Optional[dict[str, str]]:
        """Look up metadata for a miot entity (property or action).

        Returns a dict with description/icon/device_class keys, or None
        if no metadata was found.
        """
        urn = entity.extras.get("urn")
        if urn is None:
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

        type_dict: Optional[dict] = getattr(serv, type_, None)
        if type_dict is None:
            _LOGGER.debug("No metadata type %s in service %s", type_, service_name)
            return None

        meta: Optional[MetaBase] = type_dict.get(entity_name)
        if meta is None:
            _LOGGER.debug("No metadata for %s", full_name)
            return None

        result: dict[str, str] = {}
        if meta.description:
            result["description"] = meta.description
        if meta.icon:
            result["icon"] = meta.icon
        if meta.device_class:
            result["device_class"] = meta.device_class

        _LOGGER.debug("Found metadata for %s: %s", full_name, result)
        return result
