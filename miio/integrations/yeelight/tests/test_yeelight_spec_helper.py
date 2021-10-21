from ..spec_helper import ColorTempRange, YeelightSpecHelper


def test_get_model_info():
    spec_helper = YeelightSpecHelper()
    model_info = spec_helper.get_model_info("yeelink.light.bslamp1")
    assert model_info.model == "yeelink.light.bslamp1"
    assert model_info.color_temp == ColorTempRange(1700, 6500)
    assert model_info.night_light is False
    assert model_info.background_light is False
    assert model_info.supports_color is True


def test_get_unknown_model_info():
    spec_helper = YeelightSpecHelper()
    model_info = spec_helper.get_model_info("notreal")
    assert model_info.model == "generic"
    assert model_info.color_temp == ColorTempRange(1700, 6500)
    assert model_info.night_light is False
    assert model_info.background_light is False
    assert model_info.supports_color is False
