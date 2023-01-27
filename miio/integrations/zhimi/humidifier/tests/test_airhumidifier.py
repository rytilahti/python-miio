import pytest

from miio import DeviceException, DeviceInfo
from miio.tests.dummies import DummyDevice

from .. import AirHumidifier
from ..airhumidifier import (
    MODEL_HUMIDIFIER_CA1,
    MODEL_HUMIDIFIER_CB1,
    MODEL_HUMIDIFIER_V1,
    LedBrightness,
    OperationMode,
)


class DummyAirHumidifier(DummyDevice, AirHumidifier):
    def __init__(self, model, *args, **kwargs):
        self._model = model
        self.dummy_device_info = {
            "token": "68ffffffffffffffffffffffffffffff",
            "otu_stat": [101, 74, 5343, 0, 5327, 407],
            "mmfree": 228248,
            "netif": {
                "gw": "192.168.0.1",
                "localIp": "192.168.0.25",
                "mask": "255.255.255.0",
            },
            "ott_stat": [0, 0, 0, 0],
            "model": "zhimi.humidifier.v1",
            "cfg_time": 0,
            "life": 575661,
            "ap": {"rssi": -35, "ssid": "ap", "bssid": "FF:FF:FF:FF:FF:FF"},
            "wifi_fw_ver": "SD878x-14.76.36.p84-702.1.0-WM",
            "hw_ver": "MW300",
            "ot": "otu",
            "mac": "78:11:FF:FF:FF:FF",
        }

        # Special version handling for CA1
        self.dummy_device_info["fw_ver"] = (
            "1.6.6" if self._model == MODEL_HUMIDIFIER_CA1 else "1.2.9_5033"
        )

        self.state = {
            "power": "on",
            "mode": "medium",
            "temp_dec": 294,
            "humidity": 33,
            "buzzer": "off",
            "led_b": 2,
            "child_lock": "on",
            "limit_hum": 40,
            "use_time": 941100,
            "hw_version": 0,
        }

        self.return_values = {
            "get_prop": self._get_state,
            "set_power": lambda x: self._set_state("power", x),
            "set_mode": lambda x: self._set_state("mode", x),
            "set_led_b": lambda x: self._set_state("led_b", [int(x[0])]),
            "set_buzzer": lambda x: self._set_state("buzzer", x),
            "set_child_lock": lambda x: self._set_state("child_lock", x),
            "set_limit_hum": lambda x: self._set_state("limit_hum", x),
            "set_dry": lambda x: self._set_state("dry", x),
            "miIO.info": self._get_device_info,
        }

        if model == MODEL_HUMIDIFIER_V1:
            # V1 has some extra properties that are not currently tested
            self.state["trans_level"] = 85
            self.state["button_pressed"] = "led"

            # V1 doesn't support try, so return an error
            def raise_error():
                raise DeviceException("v1 does not support set_dry")

            self.return_values["set_dry"] = lambda x: raise_error()

        elif model in [MODEL_HUMIDIFIER_CA1, MODEL_HUMIDIFIER_CB1]:
            # Additional attributes of the CA1 & CB1
            extra_states = {
                "speed": 100,
                "depth": 60,
                "dry": "off",
            }
            self.state.update(extra_states)

            # CB1 reports temperature differently
            if self._model == MODEL_HUMIDIFIER_CB1:
                self.state["temperature"] = self.state["temp_dec"] / 10.0
                del self.state["temp_dec"]

        super().__init__(args, kwargs)

    def _get_device_info(self, _):
        """Return dummy device info."""
        return self.dummy_device_info


@pytest.fixture(
    params=[MODEL_HUMIDIFIER_V1, MODEL_HUMIDIFIER_CA1, MODEL_HUMIDIFIER_CB1]
)
def dev(request):
    yield DummyAirHumidifier(model=request.param)
    # TODO add ability to test on a real device


def test_on(dev):
    dev.off()  # ensure off
    assert dev.status().is_on is False

    dev.on()
    assert dev.status().is_on is True


def test_off(dev):
    dev.on()  # ensure on
    assert dev.status().is_on is True

    dev.off()
    assert dev.status().is_on is False


def test_set_mode(dev):
    def mode():
        return dev.status().mode

    dev.set_mode(OperationMode.Silent)
    assert mode() == OperationMode.Silent

    dev.set_mode(OperationMode.Medium)
    assert mode() == OperationMode.Medium

    dev.set_mode(OperationMode.High)
    assert mode() == OperationMode.High


def test_set_led(dev):
    def led_brightness():
        return dev.status().led_brightness

    dev.set_led(True)
    assert led_brightness() == LedBrightness.Bright

    dev.set_led(False)
    assert led_brightness() == LedBrightness.Off


def test_set_buzzer(dev):
    def buzzer():
        return dev.status().buzzer

    dev.set_buzzer(True)
    assert buzzer() is True

    dev.set_buzzer(False)
    assert buzzer() is False


def test_status_without_temperature(dev):
    key = "temperature" if dev.model == MODEL_HUMIDIFIER_CB1 else "temp_dec"
    dev.state[key] = None

    assert dev.status().temperature is None


def test_status_without_led_brightness(dev):
    dev.state["led_b"] = None

    assert dev.status().led_brightness is None


def test_set_target_humidity(dev):
    def target_humidity():
        return dev.status().target_humidity

    dev.set_target_humidity(30)
    assert target_humidity() == 30
    dev.set_target_humidity(60)
    assert target_humidity() == 60
    dev.set_target_humidity(80)
    assert target_humidity() == 80

    with pytest.raises(ValueError):
        dev.set_target_humidity(-1)

    with pytest.raises(ValueError):
        dev.set_target_humidity(20)

    with pytest.raises(ValueError):
        dev.set_target_humidity(90)

    with pytest.raises(ValueError):
        dev.set_target_humidity(110)


def test_set_child_lock(dev):
    def child_lock():
        return dev.status().child_lock

    dev.set_child_lock(True)
    assert child_lock() is True

    dev.set_child_lock(False)
    assert child_lock() is False


def test_status(dev):
    assert dev.status().is_on is True
    assert dev.status().humidity == dev.start_state["humidity"]
    assert dev.status().mode == OperationMode(dev.start_state["mode"])
    assert dev.status().led_brightness == LedBrightness(dev.start_state["led_b"])
    assert dev.status().buzzer == (dev.start_state["buzzer"] == "on")
    assert dev.status().child_lock == (dev.start_state["child_lock"] == "on")
    assert dev.status().target_humidity == dev.start_state["limit_hum"]

    if dev.model == MODEL_HUMIDIFIER_CB1:
        assert dev.status().temperature == dev.start_state["temperature"]
    else:
        assert dev.status().temperature == dev.start_state["temp_dec"] / 10.0

    if dev.model == MODEL_HUMIDIFIER_V1:
        # Extra props only on v1
        assert dev.status().trans_level == dev.start_state["trans_level"]
        assert dev.status().button_pressed == dev.start_state["button_pressed"]

        assert dev.status().motor_speed is None
        assert dev.status().depth is None
        assert dev.status().dry is None
        assert dev.status().water_level is None
        assert dev.status().water_tank_detached is None

    if dev.model in [MODEL_HUMIDIFIER_CA1, MODEL_HUMIDIFIER_CB1]:
        assert dev.status().motor_speed == dev.start_state["speed"]
        assert dev.status().depth == dev.start_state["depth"]
        assert dev.status().water_level == int(dev.start_state["depth"] / 1.2)
        assert dev.status().water_tank_detached == (dev.start_state["depth"] == 127)
        assert dev.status().dry == (dev.start_state["dry"] == "on")

        # Extra props only on v1 should be none now
        assert dev.status().trans_level is None
        assert dev.status().button_pressed is None

    assert dev.status().use_time == dev.start_state["use_time"]
    assert dev.status().hardware_version == dev.start_state["hw_version"]

    device_info = DeviceInfo(dev.dummy_device_info)
    assert dev.status().firmware_version == device_info.firmware_version
    assert (
        dev.status().firmware_version_major
        == device_info.firmware_version.rsplit("_", 1)[0]
    )

    try:
        version_minor = int(device_info.firmware_version.rsplit("_", 1)[1])
    except IndexError:
        version_minor = 0

    assert dev.status().firmware_version_minor == version_minor
    assert dev.status().strong_mode_enabled is False


def test_set_led_brightness(dev):
    def led_brightness():
        return dev.status().led_brightness

    dev.set_led_brightness(LedBrightness.Bright)
    assert led_brightness() == LedBrightness.Bright

    dev.set_led_brightness(LedBrightness.Dim)
    assert led_brightness() == LedBrightness.Dim

    dev.set_led_brightness(LedBrightness.Off)
    assert led_brightness() == LedBrightness.Off


def test_set_dry(dev):
    def dry():
        return dev.status().dry

    # set_dry is not supported on V1
    if dev.model == MODEL_HUMIDIFIER_V1:
        assert dry() is None
        with pytest.raises(DeviceException):
            dev.set_dry(True)

        return

    dev.set_dry(True)
    assert dry() is True

    dev.set_dry(False)
    assert dry() is False


@pytest.mark.parametrize(
    "depth,expected", [(-1, 0), (0, 0), (60, 50), (120, 100), (125, 100), (127, None)]
)
def test_water_level(dev, depth, expected):
    """Test the water level conversions."""
    if dev.model == MODEL_HUMIDIFIER_V1:
        # Water level is always none for v1
        assert dev.status().water_level is None
        return

    dev.state["depth"] = depth
    assert dev.status().water_level == expected
