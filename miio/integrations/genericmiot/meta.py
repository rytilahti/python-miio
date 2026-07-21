import logging
from pathlib import Path

import yaml

try:
    from pydantic.v1 import BaseModel
except ImportError:
    from pydantic import BaseModel

from miio.miot_models import MiotBaseModel

_LOGGER = logging.getLogger(__name__)
_ANY_SERVICE = "__ANY__"


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

    description: str | None = None  # type: ignore[assignment]
    action: dict[str, ActionMeta] | None = None
    property: dict[str, PropertyMeta] | None = None
    event: dict | None = None

    class Config:
        extra = "forbid"


class Namespace(MetaBase):
    """A namespace (e.g. miot-spec-v2) containing service definitions."""

    fallback: str | None = None
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

    def _lookup_in_namespace(
        self, ns: "Namespace", service_name: str, type_: str, entity_name: str
    ) -> MetaBase | None:
        """Look up metadata within a single namespace, following fallback if needed."""
        if ns.services is not None:
            for svc_name in (service_name, _ANY_SERVICE):
                serv = ns.services.get(svc_name)
                if serv is not None:
                    type_dict: dict | None = getattr(serv, type_, None)
                    if type_dict is not None:
                        meta: MetaBase | None = type_dict.get(entity_name)
                        if meta is not None:
                            return meta

        common = self.namespaces.get("common")
        fallback_ns = self.namespaces.get(ns.fallback or "common", common)

        if fallback_ns is not None and fallback_ns is not ns:
            return self._lookup_in_namespace(
                fallback_ns, service_name, type_, entity_name
            )

        return None

    def get_metadata(self, entity: MiotBaseModel) -> MetaBase | None:
        """Look up metadata for a miot entity (property or action).

        Returns a MetaBase object, or None if no metadata was found.
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

        ns = self.namespaces.get(ns_name, self.namespaces["common"])

        meta = self._lookup_in_namespace(ns, service_name, type_, entity_name)
        if meta is None:
            _LOGGER.debug("No metadata for %s", full_name)
            return None

        _LOGGER.debug("Found metadata for %s: %s", full_name, meta)
        return meta
