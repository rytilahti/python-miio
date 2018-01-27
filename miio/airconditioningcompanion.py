from .device import Device
import enum
from typing import Optional


class OperationMode(enum.Enum):
    Heat = 0
    Cool = 1
    Auto = 2
    Dehumidify = 3
    Ventilate = 4


class FanSpeed(enum.Enum):
    Low = 0
    Medium = 1
    High = 2
    Auto = 3


class SwingMode(enum.Enum):
    On = 0
    Off = 1


class Power(enum.Enum):
    On = 1
    Off = 0


STORAGE_SLOT_ID = 30
POWER_OFF = 'off'

# Command templates per model number (f.e. 0180111111)
# [po], [mo], [wi], [sw], [tt], [tt1], [tt4] and [tt7] are markers which will be replaced
DEVICE_COMMAND_TEMPLATES = {
    'fallback': {
        'deviceType': 'generic',
        'base': '[po][mo][wi][sw][tt]a0'
    },
    '0180111111': {
        'deviceType': 'media_1',
        'base': '[po][mo][wi][sw][tt]02'
    },
    '0180222221': {
        'deviceType': 'gree_1',
        'base': '[po][mo][wi][sw][tt]02'
    },
    '0100010727': {
        'deviceType': 'gree_2',
        'base': '[po][mo][wi][sw][tt]1100190[tt1]205002102000[tt7]0190[tt1]207002000000[tt4]0',
        'off': '01011101004000205002112000D04000207002000000A0'
    },
    '0100004795': {
        'deviceType': 'gree_8',
        'base': '[po][mo][wi][sw][tt]0100090900005002'
    },
    '0180333331': {
        'deviceType': 'haier_1',
        'base': '[po][mo][wi][sw][tt]12'
    },
    '0180666661': {
        'deviceType': 'aux_1',
        'base': '[po][mo][wi][sw][tt]12'
    },
    '0180777771': {
        'deviceType': 'chigo_1',
        'base': '[po][mo][wi][sw][tt]12'
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
    def temperature(self) -> Optional[int]:
        """Current temperature."""
        try:
            return int(self.data[1][6:8], 16)
        except TypeError:
            return None

    @property
    def swing_mode(self) -> bool:
        """True if swing mode is enabled."""
        return self.data[1][5:6] == '0'

    @property
    def fan_speed(self) -> Optional[FanSpeed]:
        """Current fan speed."""
        try:
            speed = int(self.data[1][4:5])
            return FanSpeed(speed)
        except TypeError:
            return None

    @property
    def mode(self) -> Optional[OperationMode]:
        """Current operation mode."""
        try:
            mode = int(self.data[1][3:4])
            return OperationMode(mode)
        except TypeError:
            return None


class AirConditioningCompanion(Device):
    """Main class representing Xiaomi Air Conditioning Companion."""

    def status(self) -> AirConditioningCompanionStatus:
        """Return device status."""
        status = self.send("get_model_and_state", [])
        return AirConditioningCompanionStatus(status)

    def learn(self, slot: int=STORAGE_SLOT_ID):
        """Learn an infrared command."""
        return self.send("start_ir_learn", [slot])

    def learn_result(self):
        """Read the learned command."""
        return self.send("get_ir_learn_result", [])

    def learn_stop(self, slot: int=STORAGE_SLOT_ID):
        """Stop learning of a infrared command."""
        return self.send("end_ir_learn", [slot])

    def send_ir_code(self, command: str):
        """Play a captured command.

        :param str command: Command to execute"""
        return self.send("send_ir_code", [str(command)])

    def send_command(self, command: str):
        """Send a command to the air conditioner.

        :param str command: Command to execute"""
        return self.send("send_cmd", [str(command)])

    def send_configuration(self, model: str, power: Power,
                           operation_mode: OperationMode,
                           target_temperature: float, fan_speed: FanSpeed,
                           swing_mode: SwingMode):

        # Static turn off command available?
        if (power is False) and (model in DEVICE_COMMAND_TEMPLATES) and \
                (POWER_OFF in DEVICE_COMMAND_TEMPLATES[model]):
            return self.send_command(
                model + DEVICE_COMMAND_TEMPLATES[model][POWER_OFF])

        if model in DEVICE_COMMAND_TEMPLATES:
            configuration = model + DEVICE_COMMAND_TEMPLATES[model]['base']
        else:
            configuration = \
                model + DEVICE_COMMAND_TEMPLATES['fallback']['base']

        configuration = configuration.replace('[po]', str(power.value))
        configuration = configuration.replace('[mo]', str(operation_mode.value))
        configuration = configuration.replace('[wi]', str(fan_speed.value))
        configuration = configuration.replace('[sw]', str(swing_mode.value))
        configuration = configuration.replace(
            '[tt]', hex(int(target_temperature))[2:])

        temperature = (1 + int(target_temperature) - 17) % 16
        temperature = hex(temperature)[2:].upper()
        configuration = configuration.replace('[tt1]', temperature)

        temperature = (4 + int(target_temperature) - 17) % 16
        temperature = hex(temperature)[2:].upper()
        configuration = configuration.replace('[tt4]', temperature)

        temperature = (7 + int(target_temperature) - 17) % 16
        temperature = hex(temperature)[2:].upper()
        configuration = configuration.replace('[tt7]', temperature)

        return self.send_command(configuration)
