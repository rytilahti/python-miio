from unittest.mock import Mock

import pytest

from miio.miot_models import URN, MiotBaseModel

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


class TestMetadataLoading:
    def test_load_default(self, meta: Metadata) -> None:
        assert "miot-spec-v2" in meta.namespaces
        assert "dreame-spec" in meta.namespaces

    def test_miotspec_services(self, meta: Metadata) -> None:
        ns = meta.namespaces["miot-spec-v2"]
        assert ns.services is not None
        assert "battery" in ns.services
        assert "vacuum" in ns.services
        assert "filter" in ns.services
        assert "brush-cleaner" in ns.services
        assert "identify" in ns.services
        assert "light" in ns.services

    def test_dreamespec_services(self, meta: Metadata) -> None:
        ns = meta.namespaces["dreame-spec"]
        assert ns.services is not None
        assert "vacuum-extend" in ns.services
        assert "do-not-disturb" in ns.services
        assert "audio" in ns.services
        assert "clean-logs" in ns.services


class TestMetadataLookup:
    def test_property_found(self, meta: Metadata) -> None:
        entity: MiotBaseModel = _make_entity(
            "miot-spec-v2", "property", "battery-level", "battery"
        )
        result: MetaBase | None = meta.get_metadata(entity)
        assert result is not None
        assert result.description == "Battery level"

    def test_action_found(self, meta: Metadata) -> None:
        entity: MiotBaseModel = _make_entity(
            "miot-spec-v2", "action", "start-sweep", "vacuum"
        )
        result: MetaBase | None = meta.get_metadata(entity)
        assert result is not None
        assert result.description == "Start cleaning"

    def test_unknown_namespace(self, meta: Metadata) -> None:
        entity: MiotBaseModel = _make_entity(
            "nonexistent", "property", "battery-level", "battery"
        )
        result: MetaBase | None = meta.get_metadata(entity)
        assert result is None

    def test_unknown_service(self, meta: Metadata) -> None:
        entity: MiotBaseModel = _make_entity(
            "miot-spec-v2", "property", "battery-level", "nonexistent"
        )
        result: MetaBase | None = meta.get_metadata(entity)
        assert result is None

    def test_unknown_property(self, meta: Metadata) -> None:
        entity: MiotBaseModel = _make_entity(
            "miot-spec-v2", "property", "nonexistent", "battery"
        )
        result: MetaBase | None = meta.get_metadata(entity)
        assert result is None

    def test_no_urn_in_extras(self, meta: Metadata) -> None:
        entity: Mock = Mock(spec=MiotBaseModel)
        entity.extras = {}
        result: MetaBase | None = meta.get_metadata(entity)
        assert result is None

    def test_dreame_property(self, meta: Metadata) -> None:
        entity: MiotBaseModel = _make_entity(
            "dreame-spec", "property", "mop-mode", "vacuum-extend"
        )
        result: MetaBase | None = meta.get_metadata(entity)
        assert result is not None
        assert result.description == "Mop mode"

    def test_dreame_action(self, meta: Metadata) -> None:
        entity: MiotBaseModel = _make_entity(
            "dreame-spec", "action", "stop-clean", "vacuum-extend"
        )
        result: MetaBase | None = meta.get_metadata(entity)
        assert result is not None
        assert result.description == "Stop cleaning"
