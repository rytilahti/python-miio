from pathlib import Path
from unittest.mock import Mock

import pytest

from miio.descriptors import AccessFlags, ActionDescriptor
from miio.miot_models import URN, MiotBaseModel

from ..genericmiot import GenericMiot
from ..meta import MetaBase, Metadata


@pytest.fixture(scope="module")
def meta() -> Metadata:
    return Metadata.load()


def _make_entity(
    namespace: str, type_: str, name: str, service_name: str
) -> MiotBaseModel:
    """Create a mock MiotBaseModel entity for metadata lookups."""
    urn: URN = URN.validate(f"urn:{namespace}:{type_}:{name}:1:mock:1")
    service: Mock = Mock()
    service.name = service_name
    entity: Mock = Mock()
    entity.extras = {"urn": urn}
    entity.service = service
    return entity


def test_load_default(meta: Metadata) -> None:
    assert "miot-spec-v2" in meta.namespaces
    assert "dreame-spec" in meta.namespaces


def test_miotspec_services(meta: Metadata) -> None:
    ns = meta.namespaces["miot-spec-v2"]
    assert ns.services is not None
    assert "battery" in ns.services
    assert "vacuum" in ns.services
    assert "filter" in ns.services
    assert "brush-cleaner" in ns.services
    assert "identify" in ns.services
    assert "light" in ns.services


def test_dreamespec_services(meta: Metadata) -> None:
    ns = meta.namespaces["dreame-spec"]
    assert ns.services is not None
    assert "vacuum-extend" in ns.services
    assert "do-not-disturb" in ns.services
    assert "audio" in ns.services
    assert "clean-logs" in ns.services


def test_property_found(meta: Metadata) -> None:
    entity: MiotBaseModel = _make_entity(
        "miot-spec-v2", "property", "battery-level", "battery"
    )
    result: MetaBase | None = meta.get_metadata(entity)
    assert result is not None
    assert result.description == "Battery level"


def test_action_found(meta: Metadata) -> None:
    entity: MiotBaseModel = _make_entity(
        "miot-spec-v2", "action", "start-sweep", "vacuum"
    )
    result: MetaBase | None = meta.get_metadata(entity)
    assert result is not None
    assert result.description == "Start cleaning"


def test_unknown_namespace_falls_back_to_common(meta: Metadata) -> None:
    entity: MiotBaseModel = _make_entity(
        "unknown-spec", "property", "temperature", "environment"
    )
    result: MetaBase | None = meta.get_metadata(entity)
    assert result is not None
    assert result.description == "Temperature"


def test_unknown_service(meta: Metadata) -> None:
    entity: MiotBaseModel = _make_entity(
        "miot-spec-v2", "property", "battery-level", "nonexistent"
    )
    result: MetaBase | None = meta.get_metadata(entity)
    assert result is None


def test_unknown_property(meta: Metadata) -> None:
    entity: MiotBaseModel = _make_entity(
        "miot-spec-v2", "property", "nonexistent", "battery"
    )
    result: MetaBase | None = meta.get_metadata(entity)
    assert result is None


def test_no_urn_in_extras(meta: Metadata) -> None:
    entity: Mock = Mock(spec=MiotBaseModel)
    entity.extras = {}
    result: MetaBase | None = meta.get_metadata(entity)
    assert result is None


def test_dreame_property(meta: Metadata) -> None:
    entity: MiotBaseModel = _make_entity(
        "dreame-spec", "property", "mop-mode", "vacuum-extend"
    )
    result: MetaBase | None = meta.get_metadata(entity)
    assert result is not None
    assert result.description == "Mop mode"


def test_dreame_action(meta: Metadata) -> None:
    entity: MiotBaseModel = _make_entity(
        "dreame-spec", "action", "stop-clean", "vacuum-extend"
    )
    result: MetaBase | None = meta.get_metadata(entity)
    assert result is not None
    assert result.description == "Stop cleaning"


def test_fallback_namespace() -> None:
    fallback_ns = {
        "description": "fallback",
        "services": {
            "vacuum": {
                "description": "Vacuum service",
                "property": {
                    "status": {"description": "Status from fallback"},
                },
            }
        },
    }
    primary_ns = {"description": "primary", "fallback": "fallback-ns"}
    common_ns = {"description": "common"}
    meta = Metadata(
        namespaces={
            "primary-ns": primary_ns,
            "fallback-ns": fallback_ns,
            "common": common_ns,
        }
    )

    entity = _make_entity("primary-ns", "property", "status", "vacuum")
    result = meta.get_metadata(entity)
    assert result is not None
    assert result.description == "Status from fallback"


def test_implicit_common_fallback() -> None:
    common_ns = {
        "description": "common",
        "services": {
            "__ANY__": {"property": {"brightness": {"description": "Brightness"}}}
        },
    }
    primary_ns = {"description": "primary"}
    meta = Metadata(namespaces={"primary-ns": primary_ns, "common": common_ns})

    entity = _make_entity("primary-ns", "property", "brightness", "light")
    result = meta.get_metadata(entity)
    assert result is not None
    assert result.description == "Brightness"


def test_dreamespec_falls_back_to_miotspec(meta: Metadata) -> None:
    entity = _make_entity("dreame-spec", "property", "battery-level", "battery")
    result = meta.get_metadata(entity)
    assert result is not None
    assert result.description == "Battery level"


def test_miotspec_falls_back_to_common(meta: Metadata) -> None:
    entity = _make_entity("miot-spec-v2", "property", "cleaning-time", "vacuum")
    result = meta.get_metadata(entity)
    assert result is not None
    assert result.description == "Time cleaned"


def test_dreamespec_falls_back_to_common(meta: Metadata) -> None:
    entity = _make_entity("dreame-spec", "property", "cleaning-time", "battery")
    result = meta.get_metadata(entity)
    assert result is not None
    assert result.description == "Time cleaned"


def test_load_explicit_file() -> None:
    base = Path(__file__).resolve().parent.parent / "metadata" / "base.yaml"
    meta = Metadata.load(file=base)
    assert "miot-spec-v2" in meta.namespaces


def test_no_service_returns_none(meta: Metadata) -> None:
    entity: Mock = Mock(spec=MiotBaseModel)
    entity.extras = {
        "urn": URN.validate("urn:miot-spec-v2:property:battery-level:1:mock:1")
    }
    entity.service = None
    assert meta.get_metadata(entity) is None


@pytest.fixture
def device(meta: Metadata) -> GenericMiot:
    dev = GenericMiot("127.0.0.1", "0" * 32)
    dev._meta = meta
    return dev


def test_enrich_no_metadata(device: GenericMiot) -> None:
    entity = _make_entity("unknown-ns", "action", "nonexistent", "nonexistent")
    desc = ActionDescriptor(id="test", name="nonexistent", access=AccessFlags.Execute)
    result = device._enrich_with_metadata(entity, desc)
    assert result is desc


def test_enrich_same_name(device: GenericMiot) -> None:
    entity = _make_entity("miot-spec-v2", "action", "start-sweep", "vacuum")
    desc = ActionDescriptor(
        id="test", name="Start cleaning", access=AccessFlags.Execute
    )
    result = device._enrich_with_metadata(entity, desc)
    assert result is desc


def test_enrich_applies_metadata(device: GenericMiot) -> None:
    entity = _make_entity("miot-spec-v2", "action", "start-sweep", "vacuum")
    desc = ActionDescriptor(id="test", name="start-sweep", access=AccessFlags.Execute)
    result = device._enrich_with_metadata(entity, desc)

    assert result is not desc
    assert result.name == "Start cleaning"
    assert result.extras["original"] is desc
    assert result.extras["original"].name == "start-sweep"
