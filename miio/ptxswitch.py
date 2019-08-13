import logging
from collections import defaultdict
from typing import Dict, Any, Optional

from .click_common import command, format_output
from .device import Device


_LOGGER = logging.getLogger(__name__)


# This model name is just a guess. Please update!
MODEL_PTX_ONE_INTELLIGENT_SWITCH = '090615.switch.switch01'

# This model name is just a guess. Please update!
MODEL_PTX_TWO_INTELLIGENT_SWITCH = '090615.switch.switch02'

MODEL_PTX_THREE_INTELLIGENT_SWITCH = '090615.switch.switch03'


AVAILABLE_PROPERTIES = {
    MODEL_PTX_ONE_INTELLIGENT_SWITCH: ["is_on_1","switchname1"],
    MODEL_PTX_TWO_INTELLIGENT_SWITCH: ["is_on_1","is_on_2","switchname1", "switchname2"],
    MODEL_PTX_THREE_INTELLIGENT_SWITCH: ["is_on_1","is_on_2","is_on_3","switchname1", "switchname2", "switchname3"],
}


class PtxSwitchStatus:
    # Container for status of PTX switch.

    def __init__(self, data: Dict[str, Any]) -> None:

        self.data = data


    @property
    def is_on_1(self) -> bool:
        # True if switch 1 is on.
        return self.data["is_on_1"]

    @property
    def is_on_2(self) -> Optional[bool]:
        # True if switch 2 is on.
        if "is_on_2" in self.data and self.data["is_on_2"] is not None:
            return self.data["is_on_2"]
        return None

    @property
    def is_on_3(self) -> Optional[bool]:
        # True if switch 3 is on.
        if "is_on_3" in self.data and self.data["is_on_3"] is not None:
            return self.data["is_on_3"]
        return None

    @property
    def switch_name_1(self) -> Optional[str]:
        # Name of the switch button 1
        return self.data["switchname1"]

    @property
    def switch_name_2(self) -> Optional[str]:
        # Name of the switch button 2
        if "switchname2" in self.data and self.data["switchname2"] is not None:
            return self.data["switchname2"]
        return None

    @property
    def switch_name_3(self) -> Optional[str]:
        # Name of the switch button 3
        if "switchname3" in self.data and self.data["switchname3"] is not None:
            return self.data["switchname3"]
        return None

    def __repr__(self) -> str:
        s = "<PtxSwitchStatus " \
            "is_on_1=%s, " \
            "is_on_2=%s, "\
            "is_on_3=%s, " \
            "switch_name_1=%s, " \
            "switch_name_2=%s, " \
            "switch_name_3=%s>" % \
            (self.is_on_1,
             self.is_on_2,
             self.is_on_3,
             self.switch_name_1,
             self.switch_name_2,
             self.switch_name_3)
        return s

    def __json__(self):
        return self.data


class PtxSwitch(Device):
    # Main class representing the PTX switch

    def __init__(self, ip: str = None, token: str = None, start_id: int = 0,
                 debug: int = 0, lazy_discover: bool = True,
                 model: str = MODEL_PTX_THREE_INTELLIGENT_SWITCH) -> None:
        super().__init__(ip, token, start_id, debug, lazy_discover)

        if model in AVAILABLE_PROPERTIES:
            self.model = model
        else:
            self.model = MODEL_PTX_THREE_INTELLIGENT_SWITCH

    @command(
        default_output=format_output(
            "",
            "Switch 1 Status: {result.is_on_1}\n"
            "Switch 2 Status: {result.is_on_1}\n"
            "Switch 2 Status: {result.is_on_1}\n"
            "Switch 1 Name: {result.switch_name_1}\n"
            "Switch 2 Name: {result.switch_name_1}\n"
            "Switch 3 Name: {result.switch_name_1}\n")
    )
    def status(self) -> PtxSwitchStatus:
        # Retrieve properties.
        properties = AVAILABLE_PROPERTIES[self.model].copy()
        param_list_1 = list()
        param_list_2 = list()

        # Query every channel status

        for k in properties:
            if k[:5] == "is_on":
                param_list_1.append(0)
            else:
                param_list_2.append(k)

        result_1 = self.send(
            "get_prop",
            param_list_1
        )

        param_count = len(param_list_1)
        values_count = len(result_1)
        if values_count >= param_count:
            # return values always have one more than requested.
            # get return values only we want
            result_1 = result_1[:param_count]
        else:
            result_1 = [0,0,0]
            _LOGGER.debug(
                "Count (%s) of requested params does not match the "
                "count (%s) of received values.",
                param_count, values_count)

        # Query other params
        # A single request is limited to 1 properties. Therefore the
        # properties are divided into multiple requests

        result_2 = list()
        for param in param_list_2:
            value = self.send(
                "get_prop",
                [param]
            )
            if len(value) >= 1:
                v = value[0]
                if param[:10] == "switchname":
                    if isinstance(v, str):
                        result_2.append(v)
                    else:
                        _LOGGER.debug("Unexpected type of switchname")
                        result_2.append(None)

                else:
                    result_2.append(v)

            else:
                result_2.append(None)
                _LOGGER.debug("Property %s returns None.", param)

        return PtxSwitchStatus(
            defaultdict(lambda: None,
                        zip(properties,
                            result_1 + result_2)))


    def turn_switch(self, index: int, switch_state: int) -> bool:
        """
        Turn a switch channel on/off.
        index: switch channel index, start from 1.
        switch_state: 0 means on, 1 means off.
        """
        properties = AVAILABLE_PROPERTIES[self.model]
        key = "is_on_{}".format(index)
        if key not in properties:
            _LOGGER.debug("switch index (%s) not supported.", index)
            return False

        result = self.send(
            "SetSwitch{}".format(index),
            [switch_state]
        )

        if result[:1] == 0 or result[:1] == 1:
            return True
        else:
            _LOGGER.debug("Toogle switch {} failed.".format(index))
            return False


    def turn_on_switch(self, index: int) -> bool:
        return self.turn_switch(index, 1)

    def turn_off_switch(self, index: int) -> bool:
        return self.turn_switch(index, 0)

    def set_switch_name(self, index: int, name: str) -> bool:
        """
        Set new name for a switch channel.
        index: switch channel index, start from 1.
        name: new name.
        """
        properties = AVAILABLE_PROPERTIES[self.model]
        key = "switchname{}".format(index)
        if key not in properties:
            _LOGGER.debug("switch index (%s) not supported.", index)
            return False

        result = self.send(
            "SetSwtichname{}".format(index),
            [name]
        )

        if result[:1] == 0 or result[:1] == 1:
            return True
        else:
            _LOGGER.debug(
                "Set name of switch {} failed.".format(index)
            )
            return False
