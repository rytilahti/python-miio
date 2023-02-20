from miio.descriptors import ValidSettingRange

from ..spec_helper import YeelightSpecHelper, YeelightSubLightType


def test_get_model_info():
    spec_helper = YeelightSpecHelper()
    model_info = spec_helper.get_model_info("yeelink.light.bslamp1")
    assert model_info.model == "yeelink.light.bslamp1"
    assert model_info.night_light is False
    assert model_info.lamps[YeelightSubLightType.Main].color_temp == ValidSettingRange(
        1700, 6500
    )
    assert model_info.lamps[YeelightSubLightType.Main].supports_color is True
    assert YeelightSubLightType.Background not in model_info.lamps


def test_get_unknown_model_info():
    spec_helper = YeelightSpecHelper()
    model_info = spec_helper.get_model_info("notreal")
    assert model_info.model == "yeelink.light.*"
    assert model_info.night_light is False
    assert model_info.lamps[YeelightSubLightType.Main].color_temp == ValidSettingRange(
        1700, 6500
    )
    assert model_info.lamps[YeelightSubLightType.Main].supports_color is False
    assert YeelightSubLightType.Background not in model_info.lamps
