import logging
import os
from typing import Tuple

import yaml

_LOGGER = logging.getLogger(__name__)

GENERIC_MODEL_SPEC_DICT = {
    "color_temp": (1700, 6500),
    "has_night_light": False,
    "has_background_light": False,
    "supports_color": False,
}


class YeelightModelInfo:
    model: str
    color_temp: Tuple[int, int]
    has_night_light: bool
    has_background_light: bool
    supports_color: bool

    def __init__(self, model, spec):
        self.model = model
        self.color_temp = tuple(spec.get("color_temp", (1700, 6500)))
        self.has_night_light = spec.get("night_light", False)
        self.has_background_light = spec.get("background_light", False)
        self.supports_color = spec.get("supports_color", False)


class YeelightSpecHelper:
    @staticmethod
    def specs() -> dict:
        with open(os.path.dirname(__file__) + "/specs.yaml") as filedata:
            return yaml.safe_load(filedata)

    @staticmethod
    def supported_models():
        return YeelightSpecHelper.specs().keys()

    @staticmethod
    def get_model_info(model) -> YeelightModelInfo:
        if model not in YeelightSpecHelper.specs():
            _LOGGER.warning(
                "Unknown model %s, please open an issue and supply features for this light. Returning generic information.",
                model,
            )
            return YeelightModelInfo("generic", GENERIC_MODEL_SPEC_DICT)
        return YeelightModelInfo(model, YeelightSpecHelper.specs().get(model))
