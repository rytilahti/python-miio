"""Tests for the main module."""
import pytest

import miio


@pytest.mark.parametrize(
    ("old_name", "new_name"),
    [("RoborockVacuum", "miio.integrations.roborock.vacuum.vacuum.RoborockVacuum")],
)
def test_deprecation_warning(old_name, new_name):
    """Check that deprecation warning gets emitted for deprecated imports."""
    with pytest.deprecated_call(
        match=rf"Importing {old_name} directly from 'miio' is deprecated, import <class '{new_name}'> or use DeviceFactory.create\(\) instead"
    ):
        miio.__getattr__(old_name)
