import logging
import os
from typing import List, Optional, Tuple

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
            if "color_temp" in spec:
                self.color_temp = spec["color_temp"]
            if "night_light" in spec:
                self.has_night_light = spec["night_light"]
            if "background_light" in spec:
                self.has_background_light = spec["background_light"]
            if "supports_color" in spec:
                self.supports_color = spec["supports_color"]


def specs() -> dict:
    with open(os.path.dirname(__file__) + "/specs.yaml") as filedata:
        return yaml.safe_load(filedata)


def supported_models():
    return specs().keys()


def get_model_info(model) -> YeelightModelInfo:
    if model not in specs():
        _LOGGER.warning(
            "Unknown model %s, please open an issue and supply features for this light. Returning generic information."
            % model
        )
        return YeelightModelInfo(model="generic")

    return YeelightModelInfo(model, specs().get(model))


class YeelightFlowStep:
    duration: int
    mode: int  # 1 – color, 2 – color temperature, 7 – sleep
    value: int
    brightness: int

    def __init__(self, step):
        self.duration = step["duration"]
        self.mode = step["mode"]
        self.value = step["value"]
        self.brightness = step["brightness"]


class YeelightColorFlow:
    name: str
    count: int
    # 0 means smart LED recover to the state before the color flow started.
    # 1 means smart LED stay at the state when the flow is stopped.
    # 2 means turn off the smart LED after the flow is stopped.
    action: int
    is_for_color: bool
    flow_expression: List[YeelightFlowStep]

    @property
    def expression_string(self):
        """Return a YeeLight-compatible expression that implements this flow."""
        out_string = ""
        for expression in self.flow_expression:
            if len(out_string) > 0:
                out_string += ","
            out_string += f"{expression.duration},{expression.mode},{expression.value},{expression.brightness}"
        return out_string

    def __init__(self, name, flow):
        self.name = name
        self.count = flow["count"]
        self.action = flow["action"]
        self.is_for_color = flow["is_for_color"]
        self.flow_expression = []
        for step in flow["flow_expression"]:
            self.flow_expression.append(YeelightFlowStep(step))


def flows() -> dict:
    with open(os.path.dirname(__file__) + "/color_flows.yaml") as filedata:
        return yaml.safe_load(filedata)


def supported_flows():
    return flows().keys()


def get_flow_info(name) -> Optional[YeelightColorFlow]:
    if name not in flows():
        _LOGGER.warning("Flow with name %s is underfined." % name)
        return None

    return YeelightColorFlow(name, flows().get(name))
