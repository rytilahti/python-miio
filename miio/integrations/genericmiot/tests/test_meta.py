from pathlib import Path
from unittest.mock import Mock

import pytest
import yaml

from miio.descriptors import AccessFlags, ActionDescriptor
from miio.miot_models import URN, MiotBaseModel, MiotService

from ..genericmiot import GenericMiot
from ..meta import ActionMeta, MetaBase, Metadata, Namespace, PropertyMeta, ServiceMeta


@pytest.fixture(scope="module")
def meta() -> Metadata:
    return Metadata.load()


def _make_entity(
    namespace: str, type_: str, name: str, service_name: str
) -> MiotBaseModel:
    """Create a mock MiotBaseModel entity for metadata lookups."""
    urn: URN = URN.model_validate(f"urn:{namespace}:{type_}:{name}:1:mock:1")
    service: Mock = Mock()
    service.name = service_name
    entity: Mock = Mock()
    entity.urn = urn
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


def test_unknown_namespace_falls_back_to_miotspec(meta: Metadata) -> None:
    entity: MiotBaseModel = _make_entity(
        "unknown-spec", "property", "battery-level", "battery"
    )
    result = meta.get_metadata(entity)
    assert result is not None
    assert result.description == "Battery level"


def test_unknown_namespace_falls_back_to_common(meta: Metadata) -> None:
    entity: MiotBaseModel = _make_entity(
        "unknown-spec", "property", "temperature", "environment"
    )
    result = meta.get_metadata(entity)
    assert result is not None
    assert result.description == "Temperature"


def test_registered_namespace_without_fallback_reaches_miotspec(meta: Metadata) -> None:
    meta_copy = Metadata(
        namespaces={
            **meta.namespaces,
            "no-fallback-spec": Namespace(description="no fallback"),
        }
    )
    entity = _make_entity("no-fallback-spec", "property", "battery-level", "battery")
    result = meta_copy.get_metadata(entity)
    assert result is not None
    assert result.description == "Battery level"


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
    entity.urn = URN.model_validate("urn:miot-spec-v2:property:battery-level:1:mock:1")
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


def test_namespace_merge_adds_new_service() -> None:
    base = Namespace(description="base", services={})
    stub = Namespace(
        description="stub",
        services={
            "env": ServiceMeta(
                property={"temperature": PropertyMeta(description="Temperature")}
            )
        },
    )
    base.merge(stub)
    assert "env" in base.services
    assert "temperature" in base.services["env"].property


def test_namespace_merge_adds_to_existing_service() -> None:
    base = Namespace(
        description="base",
        services={
            "env": ServiceMeta(
                property={"temperature": PropertyMeta(description="Temperature")}
            )
        },
    )
    stub = Namespace(
        description="stub",
        services={
            "env": ServiceMeta(
                property={"humidity": PropertyMeta(description="Humidity")}
            )
        },
    )
    base.merge(stub)
    assert "temperature" in base.services["env"].property
    assert "humidity" in base.services["env"].property


def test_namespace_merge_preserves_existing_descriptions() -> None:
    base = Namespace(
        description="base",
        services={
            "env": ServiceMeta(
                property={
                    "temperature": PropertyMeta(description="My custom description")
                }
            )
        },
    )
    stub = Namespace(
        description="stub",
        services={
            "env": ServiceMeta(
                property={"temperature": PropertyMeta(description="temperature")}
            )
        },
    )
    base.merge(stub)
    assert (
        base.services["env"].property["temperature"].description
        == "My custom description"
    )


def test_namespace_merge_adds_actions() -> None:
    base = Namespace(description="base", services={"settings": ServiceMeta()})
    stub = Namespace(
        description="stub",
        services={
            "settings": ServiceMeta(action={"reset": ActionMeta(description="Reset")})
        },
    )
    base.merge(stub)
    assert "reset" in base.services["settings"].action


def test_suggested_filename_uses_source_file() -> None:
    ns = Namespace(description="test", source_file="existing.yaml")
    meta = Metadata(namespaces={"my-spec": ns})
    assert meta.suggested_filename("my-spec") == "existing.yaml"


def test_suggested_filename_generates_name() -> None:
    meta = Metadata(namespaces={})
    assert meta.suggested_filename("my-new-spec") == "mynewspec.yaml"


def test_build_namespace_metadata(meta: Metadata) -> None:
    entity = _make_entity("cgllc-spec", "property", "my-prop", "settings")
    entity.description = "My property"
    entity.service.description = "Settings"  # type: ignore[union-attr]

    ns = meta.build_namespace_metadata("cgllc-spec", {"settings": [entity]})

    assert "settings" in ns.services
    assert "my-prop" in ns.services["settings"].property


def test_write_namespace_metadata_creates_file(tmp_path: Path, meta: Metadata) -> None:
    path = tmp_path / "test.yaml"
    ns = Namespace(description="Test")
    assert meta.write_namespace_metadata(ns, path) is True
    assert path.exists()


def test_write_namespace_metadata_merges_into_existing(
    tmp_path: Path, meta: Metadata
) -> None:
    path = tmp_path / "test.yaml"
    existing = Namespace(
        description="Existing",
        services={"env": ServiceMeta(property={"a": PropertyMeta(description="A")})},
    )
    path.write_text(yaml.dump(existing.model_dump(exclude_defaults=True)))

    new_ns = Namespace(
        description="New",
        services={"env": ServiceMeta(property={"b": PropertyMeta(description="B")})},
    )
    assert meta.write_namespace_metadata(new_ns, path) is False

    merged = Namespace.model_validate(yaml.safe_load(path.read_text()))
    assert "a" in merged.services["env"].property
    assert "b" in merged.services["env"].property


def test_multi_namespace_routing(tmp_path: Path, meta: Metadata) -> None:
    """Missing entities from different namespaces go to separate files."""
    ns_a = Namespace(description="ns-a", source_file="a.yaml")
    ns_b = Namespace(description="ns-b", source_file="b.yaml")
    routing_meta = Metadata(namespaces={"spec-a": ns_a, "spec-b": ns_b})

    entity_a = _make_entity("spec-a", "property", "prop", "svc")
    entity_a.description = "Prop"
    entity_a.service.description = "Svc"  # type: ignore[union-attr]

    entity_b = _make_entity("spec-b", "property", "prop", "svc")
    entity_b.description = "Prop"
    entity_b.service.description = "Svc"  # type: ignore[union-attr]

    missing_by_ns = {"spec-a": {"svc": [entity_a]}, "spec-b": {"svc": [entity_b]}}
    for ns_name, services in missing_by_ns.items():
        ns = routing_meta.build_namespace_metadata(ns_name, services)
        routing_meta.write_namespace_metadata(
            ns, tmp_path / routing_meta.suggested_filename(ns_name)
        )

    assert (tmp_path / "a.yaml").exists()
    assert (tmp_path / "b.yaml").exists()


@pytest.fixture
def battery_service() -> MiotService:
    return MiotService.model_validate_json("""{
        "iid": 2,
        "description": "Battery",
        "type": "urn:miot-spec-v2:service:battery:00000003:dummy:1",
        "properties": [{
            "iid": 1,
            "type": "urn:miot-spec-v2:property:battery-level:00000014:dummy:1",
            "description": "Battery Level",
            "format": "uint8",
            "access": ["read"]
        }],
        "actions": [],
        "events": []
    }""")


@pytest.fixture
def device_info_service() -> MiotService:
    return MiotService.model_validate_json("""{
        "iid": 1,
        "description": "Device Information",
        "type": "urn:miot-spec-v2:service:device-information:00000001:dummy:1",
        "properties": [{
            "iid": 1,
            "type": "urn:miot-spec-v2:property:manufacturer:00000001:dummy:1",
            "description": "Manufacturer",
            "format": "string",
            "access": ["read"]
        }],
        "actions": [],
        "events": []
    }""")


def _device_model(services: list) -> Mock:
    model = Mock()
    model.services = services
    return model


@pytest.mark.parametrize(
    ("meta_obj", "expected"),
    [
        (PropertyMeta(description="Battery level"), "Battery level"),
        (PropertyMeta(description=None), "(no description)"),
        (ServiceMeta(description="Battery"), "Battery"),
        (ServiceMeta(description=None), "(no description)"),
    ],
)
def test_str_representation(meta_obj, expected) -> None:
    assert str(meta_obj) == expected


def test_load_skips_missing_namespace_file(tmp_path: Path) -> None:
    base = tmp_path / "base.yaml"
    base.write_text(yaml.dump({"namespaces": {"miot-spec-v2": "nonexistent.yaml"}}))

    meta = Metadata.load(file=base)

    assert "miot-spec-v2" not in meta.namespaces


def test_build_namespace_metadata_with_action(meta: Metadata) -> None:
    entity = _make_entity("cgllc-spec", "action", "my-action", "settings")
    entity.description = "My action"
    entity.service.description = "Settings"  # type: ignore[union-attr]

    ns = meta.build_namespace_metadata("cgllc-spec", {"settings": [entity]})

    assert "my-action" in ns.services["settings"].action


def test_register_namespace(tmp_path: Path, meta: Metadata) -> None:
    base = tmp_path / "base.yaml"
    base.write_text(yaml.dump({"namespaces": {}}))

    assert meta.register_namespace("new-spec", "newspec.yaml", base) is True
    assert meta.register_namespace("new-spec", "newspec.yaml", base) is False


@pytest.mark.parametrize(
    ("ns_name", "service", "type_", "name", "expected_desc"),
    [
        ("miot-spec-v2", "battery", "property", "battery-level", "Battery level"),
        ("nonexistent-spec", "battery", "property", "battery-level", None),
    ],
)
def test_lookup_in_namespace(
    meta: Metadata, ns_name, service, type_, name, expected_desc
) -> None:
    result = meta.lookup_in_namespace(ns_name, service, type_, name)
    if expected_desc is None:
        assert result is None
    else:
        assert result is not None
        assert result.description == expected_desc


def test_collect_coverage_ok(meta: Metadata, battery_service: MiotService) -> None:
    cov = meta.collect_coverage(_device_model([battery_service]))

    assert cov.ok == 1
    assert cov.total == 1
    assert cov.missing == 0


def test_collect_coverage_fallback(
    meta: Metadata, battery_service: MiotService
) -> None:
    dreame_battery = battery_service.model_copy(deep=True)
    dreame_battery.urn.namespace = "dreame-spec"
    dreame_battery.properties[0].urn.namespace = "dreame-spec"
    cov = meta.collect_coverage(_device_model([dreame_battery]))

    assert cov.fb == 1
    assert cov.missing == 0


def test_collect_coverage_missing(meta: Metadata, battery_service: MiotService) -> None:
    unknown_service = battery_service.model_copy(deep=True)
    unknown_service.urn.namespace = "unknown-spec"
    unknown_service.urn.name = "unknown-svc"
    unknown_service.properties[0].urn.namespace = "unknown-spec"
    unknown_service.properties[0].urn.name = "unknown-prop"
    cov = meta.collect_coverage(_device_model([unknown_service]))

    assert cov.missing == 1
    assert "unknown-spec" in cov.missing_by_ns


def test_collect_coverage_no_desc(meta: Metadata, battery_service: MiotService) -> None:
    meta_no_desc = Metadata(
        namespaces={
            "miot-spec-v2": Namespace(
                description="miot-spec-v2",
                services={
                    "battery": ServiceMeta(
                        property={"battery-level": PropertyMeta(description=None)}
                    )
                },
            )
        }
    )
    cov = meta_no_desc.collect_coverage(_device_model([battery_service]))

    assert cov.no_desc == 1
    assert cov.ok == 0
    assert cov.missing == 0


def test_collect_coverage_skips_siid_1(
    meta: Metadata, device_info_service: MiotService
) -> None:
    cov = meta.collect_coverage(_device_model([device_info_service]))

    assert cov.total == 0
