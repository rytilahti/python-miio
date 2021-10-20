import logging
import os
from typing import Tuple

import yaml

_LOGGER = logging.getLogger(__name__)


class YeelightModelInfo:
    model: str
    color_temp: Tuple[int, int] = (1700, 6500)
    has_night_light: bool = False
    has_background_light: bool = False
    supports_color: bool = False

    def __init__(self, model, spec=None):
        self.model = model
        if spec:
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
            return YeelightModelInfo(model="generic")
        return YeelightModelInfo(model, YeelightSpecHelper.specs().get(model))
