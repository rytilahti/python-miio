import logging
import os
from typing import Dict, NamedTuple

import attr
import yaml

_LOGGER = logging.getLogger(__name__)


class ColorTempRange(NamedTuple):
    """Color temperature range."""

    min: int
    max: int


@attr.s(auto_attribs=True)
class YeelightModelInfo:
    model: str
    color_temp: ColorTempRange
    night_light: bool
    background_light: bool
    supports_color: bool


class YeelightSpecHelper:
    _models: Dict[str, YeelightModelInfo] = {}

    def __init__(self):
        if not YeelightSpecHelper._models:
            self._parse_specs_yaml()

    def _parse_specs_yaml(self):
        generic_info = YeelightModelInfo(
            "generic", ColorTempRange(1700, 6500), False, False, False
        )
        YeelightSpecHelper._models["generic"] = generic_info
        # read the yaml file to populate the internal model cache
        with open(os.path.dirname(__file__) + "/specs.yaml") as filedata:
            models = yaml.safe_load(filedata)
            for key, value in models.items():
                info = YeelightModelInfo(
                    key,
                    ColorTempRange(*value["color_temp"]),
                    value["night_light"],
                    value["background_light"],
                    value["supports_color"],
                )
                YeelightSpecHelper._models[key] = info

    @property
    def supported_models(self):
        return self._models.keys()

    def get_model_info(self, model) -> YeelightModelInfo:
        if model not in self._models:
            _LOGGER.warning(
                "Unknown model %s, please open an issue and supply features for this light. Returning generic information.",
                model,
            )
            return self._models["generic"]
        return self._models[model]
