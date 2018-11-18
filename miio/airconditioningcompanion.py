import enum
import logging
from typing import Optional

import click

from .click_common import command, format_output, EnumType
from .device import Device, DeviceException

_LOGGER = logging.getLogger(__name__)

MODEL_ACPARTNER_V1 = 'lumi.acpartner.v1'
MODEL_ACPARTNER_V2 = 'lumi.acpartner.v2'
MODEL_ACPARTNER_V3 = 'lumi.acpartner.v3'

MODELS_SUPPORTED = [MODEL_ACPARTNER_V1, MODEL_ACPARTNER_V2, MODEL_ACPARTNER_V3]

class AirConditioningCompanionException(DeviceException):
    pass


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
    Unknown = 2


class Power(enum.Enum):
    On = 1
    Off = 0


class Led(enum.Enum):
    On = '0'
    Off = 'A'


STORAGE_SLOT_ID = 30
POWER_OFF = 'off'

# Command templates per model number (f.e. 0180111111)
# [po], [mo], [wi], [sw], [tt], [tt1], [tt4] and [tt7] are markers which will be replaced
DEVICE_COMMAND_TEMPLATES = {
    'fallback': {
        'deviceType': 'generic',
        'base': '[po][mo][wi][sw][tt][li]'
    },
    '0100010727': {
        'deviceType': 'gree_2',
        'base': '[po][mo][wi][sw][tt]1100190[tt1]205002102000[tt7]0190[tt1]207002000000[tt4]',
        'off': '01011101004000205002112000D04000207002000000A0'
    },
    '0100004795': {
        'deviceType': 'gree_8',
        'base': '[po][mo][wi][sw][tt][li]10009090000500'
    },
    '0180333331': {
        'deviceType': 'haier_1',
        'base': '[po][mo][wi][sw][tt]1'
    },
    '0180666661': {
        'deviceType': 'aux_1',
        'base': '[po][mo][wi][sw][tt]1'
    },
    '0180777771': {
        'deviceType': 'chigo_1',
        'base': '[po][mo][wi][sw][tt]1'
    }
}


class AirConditioningCompanionStatus:
    """Container for status reports of the Xiaomi AC Companion."""

    def __init__(self, data):
        """
        Device model: lumi.acpartner.v2

        Response of "get_model_and_state":
        ['010500978022222102', '010201190280222221', '2']

        AC turned on by set_power=on:
        ['010507950000257301', '011001160100002573', '807']

        AC turned off by set_power=off:
        ['010507950000257301', '010001160100002573', '6']
        ...
        ['010507950000257301', '010001160100002573', '1']

        Example data payload:
        { 'model_and_state': ['010500978022222102', '010201190280222221', '2'],
          'power_socket': 'on' }
        """
        self.data = data
        self.model = data['model_and_state'][0]
        self.state = data['model_and_state'][1]

    @property
    def load_power(self) -> int:
        """Current power load of the air conditioner."""
        return int(self.data['model_and_state'][2])

    @property
    def power_socket(self) -> Optional[str]:
        """Current socket power state."""
        if "power_socket" in self.data and self.data["power_socket"] is not None:
            return self.data["power_socket"]

        return None

    @property
    def air_condition_model(self) -> bytes:
        """Model of the air conditioner."""
        return bytes.fromhex(self.model)

    @property
    def model_format(self) -> int:
        """Version number of the model format."""
        return self.air_condition_model[0]

    @property
    def device_type(self) -> int:
        """Device type identifier."""
        return self.air_condition_model[1]

    @property
    def air_condition_brand(self) -> int:
        """
        Brand of the air conditioner.

        Known brand ids (int) are 0182, 0097, 0037, 0202, 02782, 0197, 0192.
        """
        return int(self.air_condition_model[2:4].hex())

    @property
    def air_condition_remote(self) -> int:
        """
        Known remote ids (int):

        80111111, 80111112 (brand: 182)
        80222221 (brand: 97)
        80333331 (brand: 37)
        80444441 (brand: 202)
        80555551 (brand: 2782)
        80777771 (brand: 197)
        80666661 (brand: 192)

        """
        return int(self.air_condition_model[4:8].hex())

    @property
    def state_format(self) -> int:
        """
        Version number of the state format.

        Known values (int) are: 01, 02, 03
        """
        return int(self.air_condition_model[8])

    @property
    def air_condition_configuration(self) -> int:
        return self.state[2:10]

    @property
    def power(self) -> str:
        """Current power state."""
        return 'on' if int(self.state[2:3]) == Power.On.value else 'off'

    @property
    def led(self) -> Optional[bool]:
        """Current LED state."""
        state = self.state[8:9]
        if state == Led.On.value:
            return True

        if state == Led.Off.value:
            return False

        _LOGGER.info("Unsupported LED state: %s", state)
        return None

    @property
    def is_on(self) -> bool:
        """True if the device is turned on."""
        return self.power == 'on'

    @property
    def target_temperature(self) -> Optional[int]:
        """Target temperature."""
        try:
            return int(self.state[6:8], 16)
        except TypeError:
            return None

    @property
    def swing_mode(self) -> Optional[SwingMode]:
        """Current swing mode."""
        try:
            mode = int(self.state[5:6])
            return SwingMode(mode)
        except TypeError:
            return None

    @property
    def fan_speed(self) -> Optional[FanSpeed]:
        """Current fan speed."""
        try:
            speed = int(self.state[4:5])
            return FanSpeed(speed)
        except TypeError:
            return None

    @property
    def mode(self) -> Optional[OperationMode]:
        """Current operation mode."""
        try:
            mode = int(self.state[3:4])
            return OperationMode(mode)
        except TypeError:
            return None

    def __repr__(self) -> str:
        s = "<AirConditioningCompanionStatus " \
            "power=%s, " \
            "load_power=%s, " \
            "air_condition_model=%s, " \
            "model_format=%s, " \
            "device_type=%s, " \
            "air_condition_brand=%s, " \
            "air_condition_remote=%s, " \
            "state_format=%s, " \
            "air_condition_configuration=%s, " \
            "led=%s, " \
            "target_temperature=%s, " \
            "swing_mode=%s, " \
            "fan_speed=%s, " \
            "mode=%s>" % \
            (self.power,
             self.load_power,
             self.air_condition_model.hex(),
             self.model_format,
             self.device_type,
             self.air_condition_brand,
             self.air_condition_remote,
             self.state_format,
             self.air_condition_configuration,
             self.led,
             self.target_temperature,
             self.swing_mode,
             self.fan_speed,
             self.mode)
        return s

    def __json__(self):
        return self.data


class AirConditioningCompanion(Device):
    """Main class representing Xiaomi Air Conditioning Companion V1 and V2."""

    def __init__(self, ip: str = None, token: str = None, start_id: int = 0,
                 debug: int = 0, lazy_discover: bool = True,
                 model: str = MODEL_ACPARTNER_V2) -> None:
        super().__init__(ip, token, start_id, debug, lazy_discover)

        if model in MODELS_SUPPORTED:
            self.model = model
        else:
            self.model = MODEL_ACPARTNER_V2
            _LOGGER.error("Device model %s unsupported. Falling back to %s.", model, self.model)

    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "Load power: {result.load_power}\n"
            "Air Condition model: {result.air_condition_model}\n"
            "LED: {result.led}\n"
            "Target temperature: {result.target_temperature} °C\n"
            "Swing mode: {result.swing_mode}\n"
            "Fan speed: {result.fan_speed}\n"
            "Mode: {result.mode}\n"
        )
    )
    def status(self) -> AirConditioningCompanionStatus:
        """Return device status."""
        status = self.send("get_model_and_state")
        return AirConditioningCompanionStatus(dict(model_and_state=status))

    @command(
        default_output=format_output("Powering the air condition on"),
    )
    def on(self):
        """Turn the air condition on by infrared."""
        return self.send("set_power", ["on"])

    @command(
        default_output=format_output("Powering the air condition off"),
    )
    def off(self):
        """Turn the air condition off by infrared."""
        return self.send("set_power", ["off"])

    @command(
        click.argument("slot", type=int),
        default_output=format_output(
            "Learning infrared command into storage slot {slot}")
    )
    def learn(self, slot: int=STORAGE_SLOT_ID):
        """Learn an infrared command."""
        return self.send("start_ir_learn", [slot])

    @command(
        default_output=format_output("Reading learned infrared commands")
    )
    def learn_result(self):
        """Read the learned command."""
        return self.send("get_ir_learn_result")

    @command(
        click.argument("slot", type=int),
        default_output=format_output(
            "Learning infrared command into storage slot {slot} stopped")
    )
    def learn_stop(self, slot: int=STORAGE_SLOT_ID):
        """Stop learning of a infrared command."""
        return self.send("end_ir_learn", [slot])

    @command(
        click.argument("model", type=str),
        click.argument("code", type=str),
        default_output=format_output("Sending the supplied infrared command")
    )
    def send_ir_code(self, model: str, code: str, slot: int=0):
        """Play a captured command.

        :param str model: Air condition model
        :param str code: Command to execute
        :param int slot: Unknown internal register or slot
        """
        try:
            model = bytes.fromhex(model)
        except ValueError:
            raise AirConditioningCompanionException(
                "Invalid model. A hexadecimal string must be provided")

        try:
            code = bytes.fromhex(code)
        except ValueError:
            raise AirConditioningCompanionException(
                "Invalid code. A hexadecimal string must be provided")

        if slot < 0 or slot > 134:
            raise AirConditioningCompanionException("Invalid slot: %s" % slot)

        slot = bytes([121 + slot])

        # FE + 0487 + 00007145 + 9470 + 1FFF + 7F + FF + 06 + 0042 + 27 + 4E + 0025002D008500AC01...
        command = code[0:1] + model[2:8] + b'\x94\x70\x1F\xFF' + \
            slot + b'\xFF' + code[13:16] + b'\x27'

        checksum = sum(command) & 0xFF
        command = command + bytes([checksum]) + code[18:]

        return self.send("send_ir_code", [command.hex().upper()])

    @command(
        click.argument("command", type=str),
        default_output=format_output("Sending a command to the air conditioner")
    )
    def send_command(self, command: str):
        """Send a command to the air conditioner.

        :param str command: Command to execute"""
        return self.send("send_cmd", [str(command)])

    @command(
        click.argument("model", type=str),
        click.argument("power", type=EnumType(Power, False)),
        click.argument("operation_mode", type=EnumType(OperationMode, False)),
        click.argument("target_temperature", type=int),
        click.argument("fan_speed", type=EnumType(FanSpeed, False)),
        click.argument("swing_mode", type=EnumType(SwingMode, False)),
        click.argument("led", type=EnumType(Led, False)),
        default_output=format_output(
            "Sending a configuration to the air conditioner")
    )
    def send_configuration(self, model: str, power: Power,
                           operation_mode: OperationMode,
                           target_temperature: int, fan_speed: FanSpeed,
                           swing_mode: SwingMode, led: Led):

        prefix = str(model[0:2] + model[8:16])
        suffix = model[-1:]

        # Static turn off command available?
        if (power is Power.Off) and (prefix in DEVICE_COMMAND_TEMPLATES) and \
                (POWER_OFF in DEVICE_COMMAND_TEMPLATES[prefix]):
            return self.send_command(
                prefix + DEVICE_COMMAND_TEMPLATES[prefix][POWER_OFF])

        if prefix in DEVICE_COMMAND_TEMPLATES:
            configuration = prefix + DEVICE_COMMAND_TEMPLATES[prefix]['base']
        else:
            configuration = \
                prefix + DEVICE_COMMAND_TEMPLATES['fallback']['base']

        configuration = configuration.replace('[po]', str(power.value))
        configuration = configuration.replace('[mo]', str(operation_mode.value))
        configuration = configuration.replace('[wi]', str(fan_speed.value))
        configuration = configuration.replace('[sw]', str(swing_mode.value))
        configuration = configuration.replace('[tt]', format(target_temperature, 'X'))
        configuration = configuration.replace('[li]', str(led.value))

        temperature = format((1 + target_temperature - 17) % 16, 'X')
        configuration = configuration.replace('[tt1]', temperature)

        temperature = format((4 + target_temperature - 17) % 16, 'X')
        configuration = configuration.replace('[tt4]', temperature)

        temperature = format((7 + target_temperature - 17) % 16, 'X')
        configuration = configuration.replace('[tt7]', temperature)

        configuration = configuration + suffix

        return self.send_command(configuration)


class AirConditioningCompanionV3(AirConditioningCompanion):
    def __init__(self, ip: str = None, token: str = None, start_id: int = 0,
                 debug: int = 0, lazy_discover: bool = True) -> None:
        super().__init__(ip, token, start_id, debug, lazy_discover,
                         model=MODEL_ACPARTNER_V3)

    @command(
        default_output=format_output("Powering socket on"),
    )
    def socket_on(self):
        """Socket power on."""
        return self.send("toggle_plug", ["on"])

    @command(
        default_output=format_output("Powering socket off"),
    )
    def socket_off(self):
        """Socket power off."""
        return self.send("toggle_plug", ["off"])

    @command(
        default_output=format_output(
            "",
            "Power: {result.power}\n"
            "Power socket: {result.power_socket}\n"
            "Load power: {result.load_power}\n"
            "Air Condition model: {result.air_condition_model}\n"
            "LED: {result.led}\n"
            "Target temperature: {result.target_temperature} °C\n"
            "Swing mode: {result.swing_mode}\n"
            "Fan speed: {result.fan_speed}\n"
            "Mode: {result.mode}\n"
        )
    )
    def status(self) -> AirConditioningCompanionStatus:
        """Return device status."""
        status = self.send("get_model_and_state")
        power_socket = self.send("get_device_prop", ["lumi.0", "plug_state"])
        return AirConditioningCompanionStatus(dict(
            model_and_state=status, power_socket=power_socket))
