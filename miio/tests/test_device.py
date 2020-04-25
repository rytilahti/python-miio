import math

import pytest

from miio import Device
from miio.exceptions import DeviceInfoUnavailableException, PayloadDecodeException


@pytest.mark.parametrize("max_properties", [None, 1, 15])
def test_get_properties_splitting(mocker, max_properties):
    properties = [i for i in range(20)]

    send = mocker.patch("miio.Device.send")
    d = Device("127.0.0.1", "68ffffffffffffffffffffffffffffff")
    d.get_properties(properties, max_properties=max_properties)

    if max_properties is None:
        max_properties = len(properties)
    assert send.call_count == math.ceil(len(properties) / max_properties)


def test_unavailable_device_info_raises(mocker):
    send = mocker.patch("miio.Device.send", side_effect=PayloadDecodeException)
    d = Device("127.0.0.1", "68ffffffffffffffffffffffffffffff")

    with pytest.raises(DeviceInfoUnavailableException):
        d.info()

    assert send.call_count == 1
