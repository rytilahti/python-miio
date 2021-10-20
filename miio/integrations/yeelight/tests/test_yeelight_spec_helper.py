from unittest import TestCase

from ..spec_helper import YeelightSpecHelper


class TestYeelightSpecHelper(TestCase):
    def test_get_model_info(self):
        model_info = YeelightSpecHelper.get_model_info("yeelink.light.bslamp1")
        assert model_info.model == "yeelink.light.bslamp1"
        assert model_info.color_temp == (1700, 6500)
        assert model_info.has_night_light is False
        assert model_info.has_background_light is False
        assert model_info.supports_color is True

        model_info = YeelightSpecHelper.get_model_info("notreal")
        assert model_info.model == "generic"
        assert model_info.color_temp == (1700, 6500)
        assert model_info.has_night_light is False
        assert model_info.has_background_light is False
        assert model_info.supports_color is False
