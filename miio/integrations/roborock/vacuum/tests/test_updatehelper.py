from unittest.mock import MagicMock

from miio import DeviceException

from ..updatehelper import UpdateHelper


def test_updatehelper():
    """Test that update helper removes erroring methods from future updates."""
    main_status = MagicMock()
    second_status = MagicMock()
    unsupported = MagicMock(side_effect=DeviceException("Broken"))
    helper = UpdateHelper(main_status)
    helper.add_update_method("working", second_status)
    helper.add_update_method("broken", unsupported)

    helper.status()

    main_status.assert_called_once()
    second_status.assert_called_once()
    unsupported.assert_called_once()

    # perform second update
    helper.status()

    assert main_status.call_count == 2
    assert second_status.call_count == 2
    assert unsupported.call_count == 1
