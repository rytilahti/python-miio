"""Test of vacuum devices."""
from collections.abc import Iterable
from typing import List, Sequence, Tuple, Type

import pytest

from miio.device import Device
from miio.integrations.vacuum.roborock.vacuum import ROCKROBO_V1
from miio.interfaces import VacuumInterface

# list of all supported vacuum classes
VACUUM_CLASSES: Tuple[Type[VacuumInterface], ...] = tuple(
    cl for cl in VacuumInterface.__subclasses__()  # type: ignore
)


def _all_vacuum_models() -> Sequence[Tuple[Type[Device], str]]:
    """:return: list of tuples with supported vacuum models with corresponding class"""
    result: List[Tuple[Type[Device], str]] = []
    for cls in VACUUM_CLASSES:
        assert issubclass(cls, Device)
        vacuum_models = cls.supported_models
        assert isinstance(vacuum_models, Iterable)
        for model in vacuum_models:
            result.append((cls, model))
    return result  # type: ignore


@pytest.mark.parametrize("cls, model", _all_vacuum_models())
def test_vacuum_fan_speed_presets(cls: Type[Device], model: str) -> None:
    """Test method VacuumInterface.fan_speed_presets()"""
    if model == ROCKROBO_V1:
        return  # this model cannot be tested because presets depends on firmware
    dev = cls("127.0.0.1", "68ffffffffffffffffffffffffffffff", model=model)
    assert isinstance(dev, VacuumInterface)
    presets = dev.fan_speed_presets()
    assert presets is not None, "presets must be defined"
    assert bool(presets), "presets cannot be empty"
    assert isinstance(presets, dict), "presets must be dictionary"
    for name, value in presets.items():
        assert isinstance(name, str), "presets key must be string"
        assert name, "presets key cannot be empty"
        assert isinstance(value, int), "presets value must be integer"
        assert value >= 0, "presets value must be >= 0"


@pytest.mark.parametrize("cls, model", _all_vacuum_models())
def test_vacuum_set_fan_speed_presets_fails(cls: Type[Device], model: str) -> None:
    """Test method VacuumInterface.fan_speed_presets()"""
    if model == ROCKROBO_V1:
        return  # this model cannot be tested because presets depends on firmware
    dev = cls("127.0.0.1", "68ffffffffffffffffffffffffffffff", model=model)
    assert isinstance(dev, VacuumInterface)
    with pytest.raises(ValueError):
        dev.set_fan_speed_preset(-1)
