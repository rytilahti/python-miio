import logging
from .device import Device
import enum
from typing import Optional

_LOGGER = logging.getLogger(__name__)


class OperationMode(enum.Enum):
    Heat = 0
    Cool = 1
    Auto = 2


class FanSpeed(enum.Enum):
    Low = 0
    Medium = 1
    High = 2
    Auto = 3


STORAGE_SLOT_ID = 30


STATE_ON = 'on'
STATE_OFF = 'off'
STATE_HEAT = 'heat'
STATE_COOL = 'cool'
STATE_AUTO = 'auto'

STATE_IDLE = 'idle'
STATE_LOW = 'low'
STATE_MEDIUM = 'medium'
STATE_HIGH = 'high'

AC_DEVICE_PRESETS = {
    "default": {
        "description": "The Default Replacement of AC Partner",
        "defaultMain": "AC model(10)+po+mo+wi+sw+tt",
        "VALUE": ["po", "mo", "wi", "sw", "tt", "li"],
        "po": {
            "type": "switch",
            "on": "1",
            "off": "0"
        },
        "mo": {
            "heater": "0",
            "cooler": "1",
            "auto": "2",
            "dehum": "3",
            "airSup": "4"
        },
        "wi": {
            "auto": "3",
            "1": "0",
            "2": "1",
            "3": "2"
        },
        "sw": {
            "on": "0",
            "off": "1"
        },
        "tt": "1",
        "li": {
            "off": "a0"
        }
    },
    "0180111111": {
        "des": "media_1",
        "main": "0180111111pomowiswtt02"
    },
    "0180222221": {
        "des": "gree_1",
        "main": "0180222221pomowiswtt02"
    },
    "0100010727": {
        "des": "gree_2",
        "main": "0100010727pomowiswtt1100190t0t20500\
                2102000t6t0190t0t207002000000t4wt0",
        "off": "010001072701011101004000205002112000\
                D04000207002000000A0",
        "EXTRA_VALUE": ["t0t", "t6t", "t4wt"],
        "t0t": "1",
        "t6t": "7",
        "t4wt": "4"
    },
    "0100004795": {
        "des": "gree_8",
        "main": "0100004795pomowiswtt0100090900005002"
    },
    "0180333331": {
        "des": "haier_1",
        "main": "0180333331pomowiswtt12"
    },
    "0180666661": {
        "des": "aux_1",
        "main": "0180666661pomowiswtt12"
    },
    "0180777771": {
        "des": "chigo_1",
        "main": "0180777771pomowiswtt12"
    }
}

class AirConditioningCompanionStatus:
    """Container for status reports of the Xiaomi AC Companion."""

    def __init__(self, data):
        # Device model: lumi.acpartner.v2
        #
        # Response of "get_model_and_state":
        # ['010500978022222102', '010201190280222221', '2']
        self.data = data

    @property
    def air_condition_power(self) -> str:
        """Current power state of the air conditioner."""
        return str(self.data[2])

    @property
    def air_condition_model(self) -> str:
        """Model of the air conditioner."""
        return str(self.data[0][0:2] + self.data[0][8:16])

    @property
    def power(self) -> str:
        """Current power state."""
        return 'on' if (self.data[1][2:3] == '1') else 'off'

    @property
    def is_on(self) -> bool:
        """True if the device is turned on."""
        return self.power == 'on'

    @property
    def temperature(self) -> int:
        """Current temperature."""
        return int(self.data[1][6:8], 16)

    @property
    def swing_mode(self) -> bool:
        """True if swing mode is enabled."""
        return self.data[1][5:6] == '0'

    @property
    def fan_speed(self) -> Optional[FanSpeed]:
        """Current fan speed."""
        speed = int(self.data[1][4:5])
        if speed is not None:
            return FanSpeed(speed)

        return None

    @property
    def mode(self) -> Optional[OperationMode]:
        """Current operation mode."""
        mode = int(self.data[1][3:4])
        if mode is not None:
            return OperationMode(mode)

        return None


class AirConditioningCompanionUtility:
    """Utility class for infrared command assembly."""

    def assembleCommand(self, model: str, operation_mode: str, target_temperature: float, fan_mode: str, swing_mode: bool) -> str:
        """
        model[10]+on/off[1]+mode[1]+wi[1]+sw[1]+temp[2]+scode[2]
        0180111111 po mo wi sw tt 02
        """

        # Static turn off command available?
        if (model in AC_DEVICE_PRESETS) and (STATE_OFF in AC_DEVICE_PRESETS[model]) and ((operation_mode == STATE_OFF) or (operation_mode == STATE_IDLE)):
            return AC_DEVICE_PRESETS[model][STATE_OFF]

        if model not in AC_DEVICE_PRESETS:
            command = model + "pomowiswtta0"
        else:
            command = AC_DEVICE_PRESETS[model]['main']

        codeconfig = AC_DEVICE_PRESETS['default']
        valuecont = AC_DEVICE_PRESETS['default']['VALUE']
        index = 0
        while index < len(valuecont):
            tep = valuecont[index]
            if tep == "tt":
                temp = hex(int(target_temperature))[2:]
                command = command.replace('tt', temp)
            if tep == "po":
                if (operation_mode == STATE_IDLE) or (operation_mode == STATE_OFF):
                    pocode = codeconfig['po'][STATE_OFF]
                else:
                    pocode = codeconfig['po'][STATE_ON]
                command = command.replace('po', pocode)
            if tep == "mo":
                if operation_mode == STATE_HEAT:
                    mocode = codeconfig['mo']['heater']
                elif operation_mode == STATE_COOL:
                    mocode = codeconfig['mo']['cooler']
                else:
                    mocode = '2'
                command = command.replace('mo', mocode)
            if tep == "wi":
                if fan_mode == STATE_LOW:
                    wicode = '0'
                elif fan_mode == STATE_MEDIUM:
                    wicode = '1'
                elif fan_mode == STATE_HIGH:
                    wicode = '2'
                else:
                    wicode = '3'
                command = command.replace('wi', wicode)
            if tep == "sw":
                if swing_mode == STATE_ON:
                    command = command.replace(
                        'sw', codeconfig['sw'][STATE_ON])
                else:
                    command = command.replace(
                        'sw', codeconfig['sw'][STATE_OFF])
            # BUG: What is li and when should it be used?
            #if tep == "li":
            #    command = command.replace('li', codeconfig['li'][STATE_OFF])
            index += 1

        if (model in AC_DEVICE_PRESETS) and (
                    'EXTRA_VALUE' in AC_DEVICE_PRESETS[model]):
            codeconfig = AC_DEVICE_PRESETS[model]
            valuecont = AC_DEVICE_PRESETS[model]['EXTRA_VALUE']
            index = 0
            while index < len(valuecont):
                tep = valuecont[index]
                if tep == "t0t":
                    temp = (
                               int(codeconfig['t0t']) + int(target_temperature) - 17) % 16
                    temp = hex(temp)[2:].upper()
                    command = command.replace('t0t', temp)
                if tep == "t6t":
                    temp = (int(codeconfig['t6t']) + int(target_temperature) - 17) % 16
                    temp = hex(temp)[2:].upper()
                    command = command.replace('t6t', temp)
                if tep == "t4wt":
                    temp = (int(codeconfig['t4wt']) + int(target_temperature) - 17) % 16
                    temp = hex(temp)[2:].upper()
                    command = command.replace('t4wt', temp)
                index += 1

        return command


class AirConditioningCompanion(Device):
    """Main class representing Xiaomi Air Conditioning Companion."""

    def status(self) -> AirConditioningCompanionStatus:
        """Return device status."""
        status = self.send("get_model_and_state", [])
        return AirConditioningCompanionStatus(status)

    def learn(self):
        """Learn an infrared command."""
        return self.send("start_ir_learn", [STORAGE_SLOT_ID])

    def learn_result(self):
        """Read the learned command."""
        return self.send("get_ir_learn_result", [])

    def learn_stop(self):
        """Stop learning of a infrared command."""
        return self.send("end_ir_learn", [STORAGE_SLOT_ID])

    def send_ir_code(self, command: str):
        """Play a captured command.

        :param str command: Command to execute"""
        return self.send("send_ir_code", [str(command)])

    def send_command(self, command: str):
        """Send a command to the air conditioner.

        :param str command: Command to execute"""
        return self.send("send_cmd", [str(command)])
