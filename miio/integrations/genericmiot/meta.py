import logging
from collections import defaultdict
from pathlib import Path
from typing import NamedTuple

import yaml
from pydantic import BaseModel, ConfigDict

from miio.miot_models import DeviceModel, MiotBaseModel

_LOGGER = logging.getLogger(__name__)
_ANY_SERVICE = "__ANY__"


class CoverageResult(NamedTuple):
    """Aggregated metadata coverage for a device model."""

    total: int
    ok: int
    fb: int
    missing: int
    no_desc: int
    missing_by_ns: dict


class MetaBase(BaseModel):
    """Base metadata with description."""

    description: str
    source: str | None = None  # namespace that provided this metadata, set on lookup

    model_config = ConfigDict(extra="forbid")

    def __str__(self) -> str:
        return self.description if self.description else "(no description)"


class ActionMeta(MetaBase):
    """Metadata for actions."""

    description: str | None = None  # type: ignore[assignment]


class PropertyMeta(MetaBase):
    """Metadata for properties."""

    description: str | None = None  # type: ignore[assignment]


class ServiceMeta(MetaBase):
    """Metadata for a service, containing per-action and per-property metadata."""

    description: str | None = None  # type: ignore[assignment]
    property: dict[str, PropertyMeta] = {}
    action: dict[str, ActionMeta] = {}
    event: dict = {}

    model_config = ConfigDict(extra="forbid")

    def __str__(self) -> str:
        return self.description if self.description else "(no description)"

    def get(self, type_: str, name: str) -> MetaBase | None:
        """Return metadata for the given type and name, or None if not found."""
        return getattr(self, type_).get(name)


class Namespace(MetaBase):
    """A namespace (e.g. miot-spec-v2) containing service definitions."""

    services: dict[str, ServiceMeta] = {}
    source_file: str | None = None

    def merge(self, other: "Namespace") -> None:
        """Add entries from other that are not already present in this namespace."""
        for svc_name, other_svc in other.services.items():
            if svc_name not in self.services:
                self.services[svc_name] = other_svc
                continue

            svc = self.services[svc_name]
            for name, prop in other_svc.property.items():
                svc.property.setdefault(name, prop)
            for name, act in other_svc.action.items():
                svc.action.setdefault(name, act)


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

        missing = []
        for ns_name, ns_value in data["namespaces"].items():
            if isinstance(ns_value, str):
                ns_path = file.parent / ns_value
                if not ns_path.exists():
                    _LOGGER.warning("Namespace file not found, skipping: %s", ns_path)
                    missing.append(ns_name)
                    continue

                _LOGGER.debug("Loading namespace %s from %s", ns_name, ns_path)
                with ns_path.open() as f:
                    ns_data = yaml.safe_load(f)
                ns_data["source_file"] = ns_value
                data["namespaces"][ns_name] = ns_data

        for ns_name in missing:
            del data["namespaces"][ns_name]

        return cls(**data)

    def suggested_filename(self, ns_name: str) -> str:
        """Return the filename for a namespace metadata file."""
        ns = self.namespaces.get(ns_name)
        if ns and ns.source_file:
            return ns.source_file

        return f"{ns_name.replace('-', '')}.yaml"

    def _lookup_in_namespace(
        self, ns: "Namespace", service_name: str, type_: str, entity_name: str
    ) -> MetaBase | None:
        """Look up metadata in a namespace's own services."""
        for svc_name in (service_name, _ANY_SERVICE):
            if (serv := ns.services.get(svc_name)) and (
                meta := serv.get(type_, entity_name)
            ):
                return meta

        return None

    def build_namespace_metadata(
        self,
        ns_name: str,
        missing: dict[str, list[MiotBaseModel]],
    ) -> "Namespace":
        """Build a Namespace with template entries for entities that lack coverage."""
        services = {}
        for svc_name, entities in missing.items():
            props = {}
            acts = {}
            for entity in entities:
                if entity.urn.type == "property":
                    props[entity.urn.name] = PropertyMeta(
                        description=entity.description
                    )
                elif entity.urn.type == "action":
                    acts[entity.urn.name] = ActionMeta(description=entity.description)

            svc_desc = entities[0].service.description if entities[0].service else None
            services[svc_name] = ServiceMeta(
                description=svc_desc,
                property=props,
                action=acts,
            )

        return Namespace(
            description=f"Metadata for {ns_name} namespace",
            services=services,
        )

    def register_namespace(self, ns_name: str, filename: str, base_file: Path) -> bool:
        """Add a namespace entry to the index file if not already listed."""
        data = yaml.safe_load(base_file.read_text())
        if ns_name in data["namespaces"]:
            return False

        data["namespaces"][ns_name] = filename
        base_file.write_text(
            yaml.dump(
                data,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
            )
        )

        return True

    def write_namespace_metadata(self, ns_meta: "Namespace", path: Path) -> bool:
        """Write namespace metadata to a file, merging into any existing content."""
        created = not path.exists()
        if not created:
            existing = Namespace.model_validate(yaml.safe_load(path.read_text()))
            existing.merge(ns_meta)
            ns_meta = existing

        data = ns_meta.model_dump(exclude_defaults=True)
        for svc in data.get("services", {}).values():
            for key in ("property", "action"):
                if key in svc:
                    svc[key] = dict(sorted(svc[key].items()))

        path.write_text(
            yaml.dump(
                data, default_flow_style=False, sort_keys=False, allow_unicode=True
            )
        )

        return created

    def lookup_in_namespace(
        self, ns_name: str, service_name: str, type_: str, entity_name: str
    ) -> MetaBase | None:
        """Look up metadata in a specific namespace's own services."""
        ns = self.namespaces.get(ns_name)
        if ns is None:
            return None

        return self._lookup_in_namespace(ns, service_name, type_, entity_name)

    def collect_coverage(self, device_model: DeviceModel) -> CoverageResult:
        """Count metadata coverage for a device model and collect missing entities."""
        missing_by_ns: dict = defaultdict(dict)
        total = ok = fb = missing = no_desc = 0

        for serv in device_model.services:
            if serv.siid == 1:
                continue

            ns_name = serv.urn.namespace
            for entity in [*serv.properties, *serv.actions]:
                total += 1
                direct = self.lookup_in_namespace(
                    ns_name, serv.name, entity.urn.type, entity.urn.name
                )
                if direct:
                    if direct.description is None:
                        no_desc += 1
                    else:
                        ok += 1
                    continue

                fallback = self.get_metadata(entity)
                if fallback:
                    if fallback.description is None:
                        no_desc += 1
                    else:
                        fb += 1
                else:
                    missing += 1
                    missing_by_ns[ns_name].setdefault(serv.name, []).append(entity)

        return CoverageResult(total, ok, fb, missing, no_desc, missing_by_ns)

    def get_metadata(self, entity: MiotBaseModel) -> MetaBase | None:
        """Look up metadata for a miot entity, returning it with source namespace set."""
        if entity.service is None:
            return None

        ns_name = entity.urn.namespace
        service_name = entity.service.name

        for try_name in dict.fromkeys([ns_name, "miot-spec-v2", "common"]):
            ns = self.namespaces.get(try_name)
            if ns is None:
                continue

            meta = self._lookup_in_namespace(
                ns, service_name, entity.urn.type, entity.urn.name
            )
            if meta is not None:
                _LOGGER.debug("Found metadata for %s in %s", entity, try_name)
                return meta.model_copy(update={"source": try_name})

        _LOGGER.debug("No metadata for %s", entity)
        return None
