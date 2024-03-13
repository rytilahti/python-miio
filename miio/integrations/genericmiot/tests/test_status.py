import logging
from unittest.mock import Mock

import pytest

from ..status import GenericMiotStatus


@pytest.fixture(scope="session")
def mockdev():
    yield Mock()


VALID_RESPONSE = {"code": 0, "did": "valid-response", "piid": 1, "siid": 1, "value": 1}


@pytest.mark.parametrize("key", ("did", "piid", "siid", "value", "code"))
def test_response_with_missing_value(key, mockdev, caplog: pytest.LogCaptureFixture):
    """Verify that property responses without necessary keys are ignored."""
    caplog.set_level(logging.DEBUG)

    prop = {"code": 0, "did": f"no-{key}-in-response", "piid": 1, "siid": 1, "value": 1}
    prop.pop(key)

    status = GenericMiotStatus([VALID_RESPONSE, prop], mockdev)
    assert f"Ignoring due to missing '{key}'" in caplog.text
    assert len(status.data) == 1


@pytest.mark.parametrize("code", (-123, 123))
def test_response_with_error_codes(code, mockdev, caplog: pytest.LogCaptureFixture):
    caplog.set_level(logging.WARNING)

    did = f"error-code-{code}"
    prop = {"code": code, "did": did, "piid": 1, "siid": 1}
    status = GenericMiotStatus([VALID_RESPONSE, prop], mockdev)
    assert f"Ignoring due to error code '{code}'" in caplog.text
    assert len(status.data) == 1
