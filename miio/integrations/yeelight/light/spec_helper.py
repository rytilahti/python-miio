import logging
import os
from enum import IntEnum
from typing import Dict

import attr
import yaml

from miio.descriptors import ValidSettingRange

_LOGGER = logging.getLogger(__name__)


class YeelightSubLightType(IntEnum):
    Main = 0
    Background = 1


@attr.s(auto_attribs=True)
class YeelightLampInfo:
    color_temp: ValidSettingRange
    supports_color: bool


@attr.s(auto_attribs=True)
class YeelightModelInfo:
    model: str
    night_light: bool
    lamps: Dict[YeelightSubLightType, YeelightLampInfo]


class YeelightSpecHelper:
    _models: Dict[str, YeelightModelInfo] = {}

    def __init__(self):
        if not YeelightSpecHelper._models:
            self._parse_specs_yaml()

    def _parse_specs_yaml(self):
        # read the yaml file to populate the internal model cache
        with open(os.path.dirname(__file__) + "/specs.yaml") as filedata:
            models = yaml.safe_load(filedata)
            for key, value in models.items():
                lamps = {
                    YeelightSubLightType.Main: YeelightLampInfo(
                        ValidSettingRange(*value["color_temp"]),
                        value["supports_color"],
                    )
                }

                if "background" in value:
                    lamps[YeelightSubLightType.Background] = YeelightLampInfo(
                        ValidSettingRange(*value["background"]["color_temp"]),
                        value["background"]["supports_color"],
                    )

                info = YeelightModelInfo(key, value["night_light"], lamps)
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
            return self._models["yeelink.light.*"]
        return self._models[model]
