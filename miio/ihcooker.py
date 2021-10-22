import enum
import json
import logging
import random
import warnings
from collections import defaultdict
from typing import Optional, Union

import click
import construct as c

from .click_common import command, format_output
from .device import Device, DeviceStatus
from .exceptions import DeviceException

_LOGGER = logging.getLogger(__name__)

MODEL_EG1 = "chunmi.ihcooker.eg1"
MODEL_EXP1 = "chunmi.ihcooker.exp1"
MODEL_FW = "chunmi.ihcooker.chefnic"
MODEL_HK1 = "chunmi.ihcooker.hk1"
MODEL_KOREA1 = "chunmi.ihcooker.korea1"
MODEL_TW1 = "chunmi.ihcooker.tw1"
MODEL_V1 = "chunmi.ihcooker.v1"

MODEL_VERSION1 = [MODEL_V1, MODEL_FW, MODEL_HK1, MODEL_TW1]
MODEL_VERSION2 = [MODEL_EG1, MODEL_EXP1, MODEL_KOREA1]
SUPPORTED_MODELS = MODEL_VERSION1 + MODEL_VERSION2

DEVICE_ID = {
    MODEL_EG1: 4,
    MODEL_EXP1: 4,
    MODEL_FW: 7,
    MODEL_HK1: 2,
    MODEL_KOREA1: 5,
    MODEL_TW1: 3,
    MODEL_V1: 1,
}

RECIPE_NAME_MAX_LEN_V1 = 13
RECIPE_NAME_MAX_LEN_V2 = 28
DEFAULT_FIRE_ON_OFF = 20
DEFAULT_THRESHOLD_CELCIUS = 249
DEFAULT_TEMP_TARGET_CELCIUS = 229
DEFAULT_FIRE_LEVEL = 45
DEFAULT_PHASE_MINUTES = 50


def crc16(data: bytes, offset=0, length=None):
    """Computes 16bit CRC for IHCooker recipe profiles.

    Based on variant by Amin Saidani posted on https://stackoverflow.com/a/55850496.
    """
    if length is None:
        length = len(data)
    if (
        data is None
        or offset < 0
        or offset > len(data) - 1
        and offset + length > len(data)
    ):
        return 0
    crc = 0x0000
    for i in range(0, length):
        crc ^= data[offset + i] << 8
        for _ in range(0, 8):
            if (crc & 0x8000) > 0:
                crc = (crc << 1) ^ 0x1021
            else:
                crc = crc << 1
    return crc & 0xFFFF


class IHCookerException(DeviceException):
    pass


class StageMode(enum.IntEnum):
    """Mode for current stage of recipe."""

    FireMode = 0
    TemperatureMode = 2
    Unknown4 = 4
    TempAutoSmallPot = 8  # TODO: verify this is the right behaviour.
    Unknown10 = 10
    TempAutoBigPot = 24  # TODO: verify this is the right behaviour.
    Unknown16 = 16


class OperationMode(enum.Enum):
    """Global mode the induction cooker is currently in."""

    Error = "error"
    Finish = "finish"
    Offline = "offline"
    Pause = "pause"
    TimerPaused = "pause_time"
    Precook = "precook"
    Running = "running"
    SetClock = "set01"
    SetStartTime = "set02"
    SetCookingTime = "set03"
    Shutdown = "shutdown"
    Timing = "timing"
    Waiting = "waiting"


class ArrayDefault(c.Array):
    r"""
    Homogenous array of elements, similar to C# generic T[].

    Parses into a ListContainer (a list). Parsing and building processes an exact amount of elements. If given list has less than count elements, the array is padded with the default element. More elements raises RangeError. Size is defined as count multiplied by subcon size, but only if subcon is fixed size.

    Operator [] can be used to make Array instances (recommended syntax).

    :param count: integer or context lambda, strict amount of elements
    :param subcon: Construct instance, subcon to process individual elements
    :param default: default element to pad array with.
    :param discard: optional, bool, if set then parsing returns empty list

    :raises StreamError: requested reading negative amount, could not read enough bytes, requested writing different amount than actual data, or could not write all bytes
    :raises RangeError: specified count is not valid
    :raises RangeError: given object has different length than specified count

    Can propagate any exception from the lambdas, possibly non-ConstructError.

    Example::

        >>> d = ArrayDefault(5, Byte, 0) or Byte[5]
        >>> d.build(range(3))
        b'\x00\x01\x02\x00\x00'
        >>> d.parse(_)
        [0, 1, 2, 0, 0]
    """

    def __init__(self, count, subcon, default, discard=False):
        super(ArrayDefault, self).__init__(count, subcon, discard)
        self.default = default

    def _build(self, obj, stream, context, path):
        count = self.count
        if callable(count):
            count = count(context)
        if not 0 <= count:
            raise c.RangeError("invalid count %s" % (count,), path=path)
        if len(obj) > count:
            raise c.RangeError(
                "expected %d elements, found %d" % (count, len(obj)), path=path
            )
        retlist = c.ListContainer()

        for i, e in enumerate(obj):
            context._index = i
            buildret = self.subcon._build(e, stream, context, path)
            retlist.append(buildret)
        for i in range(len(obj), count):
            context._index = i
            buildret = self.subcon._build(self.default, stream, context, path)
            retlist.append(buildret)
        return retlist


class RebuildStream(c.Rebuild):
    r"""
    Field where building does not require a value, because the value gets recomputed when needed. Comes handy when building a Struct from a dict with missing keys. Useful for length and count fields when :class:`~construct.core.Prefixed` and :class:`~construct.core.PrefixedArray` cannot be used.

    Parsing defers to subcon. Building is defered to subcon, but it builds from a value provided by the stream until now. Size is the same as subcon, unless it raises SizeofError.

    Difference between Rebuild and RebuildStream, is that RebuildStream provides the current datastream to func.

    :param subcon: Construct instance
    :param func: lambda that works with streamed bytes up to this point.

    :raises StreamError: requested reading negative amount, could not read enough bytes, requested writing different amount than actual data, or could not write all bytes

    Can propagate any exception from the lambda, possibly non-ConstructError.
    """

    def __init__(self, subcon, func):
        super(RebuildStream, self).__init__(subcon, func)

    def _build(self, obj, stream, context, path):
        fallback = c.stream_tell(stream, path)
        c.stream_seek(stream, 0, 0, path)
        data = stream.read(fallback)
        obj = self.func(data) if callable(self.func) else self.func
        ret = self.subcon._build(obj, stream, context, path)
        return ret


# Some public v2 recipes have device_version set to 1, so estimating the profile version is non-trivial, plus one might want to convert between versions.
def profile_base(is_v1, recipe_name_encoding="GBK"):
    return c.Struct(
        c.Const(3, c.Int8un),
        "device_version" / c.Default(c.Enum(c.Int8ub, **DEVICE_ID), 1 if is_v1 else 2),
        "menu_location"
        / c.Default(c.ExprValidator(c.Int8ub, lambda o, _: 0 <= o < 10), 9),
        "recipe_name"
        / c.Default(
            c.ExprAdapter(
                c.StringEncoded(  # PaddedString wrapper does not support GBK encoding.
                    c.FixedSized(
                        RECIPE_NAME_MAX_LEN_V1 if is_v1 else RECIPE_NAME_MAX_LEN_V2,
                        c.NullStripped(c.GreedyBytes),
                    ),
                    recipe_name_encoding,
                ),
                lambda x, _: x.replace("\n", " "),
                lambda x, _: x.replace(" ", "\n"),
            ),
            "Unnamed",
        ),
        c.Padding(1) if is_v1 else c.Padding(2),
        "recipe_id" / c.Default(c.Int32ub, lambda _: random.randint(0, 2 ** 32 - 1)),
        "menu_settings"
        / c.Default(
            c.BitStruct(  # byte 37
                "save_recipe" / c.Default(c.Flag, 0),
                "confirm_start" / c.Default(c.Flag, 0),
                "menu_unknown3" / c.Default(c.Flag, 0),
                "menu_unknown4" / c.Default(c.Flag, 0),
                "menu_unknown5" / c.Default(c.Flag, 0),
                "menu_unknown6" / c.Default(c.Flag, 0),
                "menu_unknown7" / c.Default(c.Flag, 0),
                "menu_unknown8" / c.Default(c.Flag, 0),
            ),
            {},
        ),
        "duration_hours"
        / c.Rebuild(
            c.Int8ub, lambda ctx: ctx.get("duration_minutes", 0) // 60
        ),  # byte 38
        "duration_minutes"
        / c.Default(
            c.ExprAdapter(
                c.Int8ub, lambda obj, ctx: obj + ctx.duration_hours * 60, c.obj_ % 60
            ),
            60,
        ),  # byte 39
        "duration_max_hours"
        / c.Rebuild(
            c.Int8ub, lambda ctx: ctx.get("duration_max_minutes", 0) // 60
        ),  # byte 40
        "duration_max_minutes"
        / c.Default(
            c.ExprAdapter(
                c.Int8ub,
                lambda obj, ctx: obj + ctx.duration_max_hours * 60,
                c.obj_ % 60,
            ),
            0,
        ),  # byte 41
        "duration_min_hours"
        / c.Rebuild(
            c.Int8ub, lambda ctx: ctx.get("duration_min_minutes", 0) // 60
        ),  # byte 42
        "duration_min_minutes"
        / c.Default(
            c.ExprAdapter(
                c.Int8ub,
                lambda obj, ctx: obj + ctx.duration_min_hours * 60,
                c.obj_ % 60,
            ),
            0,
        ),  # byte 43
        c.Padding(2),  # byte 44, 45
        "unknown_46" / c.Default(c.Byte, 1),  # byte 46, should be set to 1
        c.Padding(7) if is_v1 else c.Padding(1),
        "stages"
        / c.Default(
            ArrayDefault(
                15,
                c.Struct(  # byte 48-168
                    "mode" / c.Default(c.Enum(c.Byte, StageMode), StageMode.FireMode),
                    "hours"
                    / c.Rebuild(
                        c.Int8ub, lambda ctx: (ctx.get("minutes", 0) // 60) + 128
                    ),
                    "minutes"
                    / c.Default(
                        c.ExprAdapter(
                            c.Int8ub,
                            decoder=lambda obj, ctx: obj + (ctx.hours - 128) * 60,
                            encoder=c.obj_ % 60,
                        ),
                        DEFAULT_PHASE_MINUTES,
                    ),
                    "temp_threshold" / c.Default(c.Int8ub, DEFAULT_THRESHOLD_CELCIUS),
                    "temp_target" / c.Default(c.Int8ub, DEFAULT_TEMP_TARGET_CELCIUS),
                    "power" / c.Default(c.Int8ub, DEFAULT_FIRE_LEVEL),
                    "fire_off" / c.Default(c.Int8ub, DEFAULT_FIRE_ON_OFF),
                    "fire_on" / c.Default(c.Int8ub, DEFAULT_FIRE_ON_OFF),
                ),
                default=dict(
                    mode=StageMode.FireMode,
                    minutes=DEFAULT_PHASE_MINUTES,
                    temp_threshold=DEFAULT_THRESHOLD_CELCIUS,
                    temp_target=DEFAULT_TEMP_TARGET_CELCIUS,
                    power=DEFAULT_FIRE_LEVEL,
                    fire_off=DEFAULT_FIRE_ON_OFF,
                    fire_on=DEFAULT_FIRE_ON_OFF,
                ),
            ),
            [],
        ),
        c.Padding(16) if is_v1 else c.Padding(6),  # byte 169-174
        "unknown175" / c.Default(c.Int8ub, 0),
        "unknown176" / c.Default(c.Int8ub, 0),
        "unknown177" / c.Default(c.Int8ub, 0),
        "crc"  # byte 178-179
        / RebuildStream(
            c.Bytes(2), crc16
        ),  # Default profiles have invalid crc, c.Checksum() raises undesired error when parsed.
    )


profile_v1 = profile_base(is_v1=True)
profile_example = dict(profile_v1.parse(profile_v1.build(dict())))
profile_keys = profile_example.keys()
stage_keys = dict(profile_example["stages"][0]).keys()
menu_keys = dict(profile_example["menu_settings"]).keys()

profile_v2 = profile_base(is_v1=False)

profile_korea = profile_base(is_v1=False, recipe_name_encoding="euc-kr")


class IHCookerStatus(DeviceStatus):
    def __init__(self, model, data):
        """Responses of a chunmi.ihcooker.exp1 (fw_ver: 1.3.6.0013):

        {'func': 'running',
         'menu': '08526963650000000000000000000000000000000000000000000000000000001e',
         'action': '033814083c',
         't_func': '000f000100000000',
         'version': '000d1404',
         'custom': '0000000100000002000000030000000400000005000000180000001a0000001e',
         'wifi_led': '01'}

        {'func': 'waiting',
         'menu': '08526963650000000000000000000000000000000000000000000000000000001e',
         'action': '012b000000',
         't_func': '000f000100000000',
         'version': '000d1404',
         'custom': '0000000100000002000000030000000400000005000000180000001a0000001e',
         'wifi_led': '01'}
        """
        self.data = data
        self.model = model
        if model not in MODEL_VERSION1 and model not in MODEL_VERSION2:
            raise IHCookerException(
                "Model %s currently unsupported, please report this on github."
                % self.model
            )

    @property
    def is_v1(self):
        return self.model in MODEL_VERSION1

    @property
    def is_v2(self):
        return self.model in MODEL_VERSION2

    @property
    def mode(self) -> OperationMode:
        """Current operation mode."""
        return OperationMode(self.data["func"])

    @property
    def recipe_id(self) -> int:
        """Selected recipe id."""
        if self.is_v1:
            cap = RECIPE_NAME_MAX_LEN_V1 * 2 + 2
        else:
            cap = RECIPE_NAME_MAX_LEN_V2 * 2 + 2
        return int(self.data["menu"][cap:], 16)

    @property
    def recipe_name(self):
        if self.is_v1:
            cap = RECIPE_NAME_MAX_LEN_V1 * 2 + 2
        else:
            cap = RECIPE_NAME_MAX_LEN_V2 * 2 + 2
        name = bytes.fromhex(self.data["menu"][2:cap]).decode("GBK").strip("\x00")
        name = name.replace("\n", " ")
        return name

    @property
    def is_error(self):
        return self.mode == OperationMode.Error

    # Action-field parsing:
    @property
    def stage(self) -> Optional[int]:
        """Cooking step/stage: one in range(15) steps."""
        if not self.is_error:
            action = self.data["action"]
            if len(action) >= 6:
                return int.from_bytes(bytes.fromhex(action[0:2]), "little")
        return None

    @property
    def temperature(self) -> Optional[int]:
        """Current temperature, if idle."""
        if not self.is_error:
            action = self.data["action"]
            if len(action) >= 6:
                return int.from_bytes(bytes.fromhex(action[2:4]), "little")
        return None

    @property
    def fire_selected(self) -> Optional[int]:
        """Selected power/fire level, differs from current acting power/fire level which
        auto-adjusts, see fire_current."""
        if not self.is_error:
            action = self.data["action"]
            if len(action) >= 6:
                return int.from_bytes(bytes.fromhex(action[4:6]), "little")
        return None

    @property
    def stage_mode(self) -> Optional[StageMode]:
        """Bit flags for current cooking stage.

        Current understanding:
        0: constant power output.
        2: Temperature control.
        4: Unknown.
        8: Temp regulation and fire hard coded for small pot, via @coolibry.
        16: Unknown.
        24: Temp regulation and fire hard coded for big pot, via @coolibry.
        """
        if not self.is_error:
            action = self.data["action"]
            if len(action) >= 8:
                return StageMode(int.from_bytes(bytes.fromhex(action[6:8]), "little"))
        return None

    @property
    def target_temp(self) -> Optional[int]:
        """Target temperature."""
        if not self.is_error:
            action = self.data["action"]
            if len(action) >= 10:
                return int.from_bytes(bytes.fromhex(action[8:10]), "little")
        return None

    # Play-field parsing
    @property
    def play_phase(self) -> Optional[int]:
        """Phase from play field."""
        if not self.is_error:
            play = self.data["play"]
            if len(play) == 18:
                return int.from_bytes(bytes.fromhex(play[0:2]), "little")
        return None

    @property
    def play_unknown_2(self) -> Optional[int]:
        """Second value from play field, remains 0, usage unknown."""
        if not self.is_error:
            play = self.data["play"]
            if len(play) == 18:
                return int.from_bytes(bytes.fromhex(play[2:4]), "little")
        return None

    @property
    def play_unknown_3(self) -> Optional[int]:
        """Third value from play field, usage unknown Fluctuates apparently randomly
        between [225, 226, 228, 229, 230, 231, 233, 234, 235]"""
        if not self.is_error:
            play = self.data["play"]
            if len(play) == 18:
                return int.from_bytes(bytes.fromhex(play[4:6]), "little")
        return None

    @property
    def fire_current(self) -> Optional[int]:
        """Appears to match actual output of induction coil."""
        if not self.is_error:
            play = self.data["play"]
            if len(play) == 18:
                return int.from_bytes(bytes.fromhex(play[6:8]), "little")
        return None

    @property
    def play_fire(self) -> Optional[int]:
        """Matches fire value of action field."""
        if not self.is_error:
            play = self.data["play"]
            if len(play) == 18:
                return int.from_bytes(bytes.fromhex(play[8:10]), "little")
        return None

    @property
    def play_temperature(self) -> Optional[int]:
        """Matches measured temperature value of action field."""
        if not self.is_error:
            play = self.data["play"]
            if len(play) == 18:
                return int.from_bytes(bytes.fromhex(play[12:14]), "little")
        return None

    @property
    def temperature_upperbound(self) -> Optional[int]:
        """Appears to be an upperbound on the estimate of the temperature."""
        if not self.is_error:
            play = self.data["play"]
            if len(play) == 18:
                return int.from_bytes(bytes.fromhex(play[14:16]), "little")
        return None

    @property
    def play_unknown_9(self) -> Optional[int]:
        """Ninth value from play field, remains zero, usage unknown."""
        if not self.is_error:
            play = self.data["play"]
            if len(play) == 18:
                return int.from_bytes(bytes.fromhex(play[16:18]), "little")
        return None

    # TODO: Fully parse timer field, perhaps cooking delay?
    @property
    def user_timer_hours(self) -> int:
        """Remaining hours of the user timer."""
        return int(self.data["t_func"][8:10], 16)

    @property
    def user_timer_minutes(self) -> int:
        """Remaining minutes of the user timer."""
        return int(self.data["t_func"][10:12], 16)

    @property
    def wifi_led_setting(self) -> Optional[bool]:
        """Blue wifi led setting at bottom of device: true if led remains on at idle."""
        if "set_wifi_led" in self.data:
            return bool(self.data["set_wifi_led"] == "01")
        else:
            return None

    @property
    def hardware_version(self) -> int:
        """Hardware version."""
        return int(self.data["version"][0:4], 16)

    @property
    def firmware_version(self) -> int:
        """Firmware version."""
        return int(self.data["version"][4:8], 16)


class IHCooker(Device):
    """Main class representing the induction cooker.

    Custom recipes can be build with the profile_v1/v2 structure.
    """

    _supported_models = SUPPORTED_MODELS

    @command(
        default_output=format_output(
            "",
            "Mode: {result.mode}\n"
            "Recipe ID: {result.recipe_id}\n"
            "Recipe Name: {result.recipe_name}\n"
            "Stage: {result.stage}\n"
            "Stage Mode: {result.stage_mode}\n"
            "Target Temp: {result.target_temp}\n"
            "Temperature: {result.temperature}\n"
            "Temperature upperbound: {result.temperature_upperbound}\n"
            "Fire selected: {result.fire_selected}\n"
            "Fire current: {result.fire_current}\n"
            "WiFi Led: {result.wifi_led_setting}\n"
            "Hardware version: {result.hardware_version}\n"
            "Firmware version: {result.firmware_version}\n",
        )
    )
    def status(self) -> IHCookerStatus:
        """Retrieve properties."""
        properties_new = [
            "func",
            "menu",
            "action",
            "t_func",
            "version",
            "profiles",
            "set_wifi_led",
            "play",
        ]
        properties_old = [
            "func",
            "menu",
            "action",
            "t_func",
            "version",
            "profiles",
            "play",
        ]

        values = self.send("get_prop", ["all"])

        if len(values) == len(properties_new):
            properties = properties_new
        elif len(values) == len(properties_old):
            properties = properties_old
        else:
            raise IHCookerException(
                "Count (%d or %d) of requested properties does not match the "
                "count (%s) of received values."
                % (len(properties_new), len(properties_old), len(values)),
            )

        return IHCookerStatus(
            self.model, defaultdict(lambda: None, zip(properties, values))
        )

    @command(
        click.argument("profile", type=str),
        click.argument("skip_confirmation", type=bool, default=False),
        default_output=format_output("Cooking profile requested."),
    )
    def start(self, profile: Union[str, c.Container, dict], skip_confirmation=False):
        """Start cooking a profile.

        :arg

        Please do not use skip_confirmation=True, as this is potentially unsafe.
        """

        profile = self._prepare_profile(profile)
        profile.menu_settings.save_recipe = False
        profile.menu_settings.confirm_start = not skip_confirmation
        if skip_confirmation:
            warnings.warn(
                "You're starting a profile without confirmation, which is a potentially unsafe."
            )
            self.send("set_start", [self._profile_obj.build(profile).hex()])
        else:
            self.send("set_menu1", [self._profile_obj.build(profile).hex()])

    @command(
        click.argument("temperature", type=int),
        click.argument("skip_confirmation", type=bool, default=False),
        click.argument("minutes", type=int, default=60),
        click.argument("power", type=int, default=DEFAULT_FIRE_LEVEL),
        click.argument("menu_location", type=int, default=9),
        default_output=format_output("Cooking with temperature requested."),
    )
    def start_temp(
        self,
        temperature,
        minutes=60,
        power=DEFAULT_FIRE_LEVEL,
        skip_confirmation=False,
        menu_location=9,
    ):
        """Start cooking at a fixed temperature and duration.

        Temperature in celcius.

        Please do not use skip_confirmation=True, as this is potentially unsafe.
        """

        profile = dict(
            recipe_name="%d Degrees" % temperature,
            menu_settings=dict(save_recipe=False, confirm_start=skip_confirmation),
            duration_minutes=minutes,
            menu_location=menu_location,
            stages=[
                dict(
                    temp_target=temperature,
                    minutes=minutes,
                    mode=StageMode.TemperatureMode,
                    power=power,
                )
            ],
        )
        profile = self._prepare_profile(profile)

        if menu_location != 9:
            self.set_menu(profile, menu_location, True)
        else:
            self.start(profile, skip_confirmation)

    @command(
        click.argument("power", type=int),
        click.argument("skip_confirmation", type=bool),
        click.argument("minutes", type=int),
        default_output=format_output("Cooking with temperature requested."),
    )
    def start_fire(self, power, minutes=60, skip_confirmation=False):
        """Start cooking at a fixed fire power and duration.

        Fire: 0-99.

        Please do not use skip_confirmation=True, as this is potentially unsafe.
        """

        if 0 < power > 100:
            raise ValueError("power should be in range [0,99].")
        profile = dict(
            recipe_name="%d fire power" % power,
            menu_settings=dict(save_recipe=False, confirm_start=skip_confirmation),
            duration_minutes=minutes,
            stages=[dict(power=power, minutes=minutes, mode=StageMode.FireMode)],
        )
        profile = self._prepare_profile(profile)
        self.start(profile, skip_confirmation)

    @command(default_output=format_output("Cooking stopped"))
    def stop(self):
        """Stop cooking."""
        self.send("set_func", ["end"])

    @command(default_output=format_output("Recipe deleted"))
    def delete_recipe(self, location):
        """Delete recipe at location [0,7]"""
        if location >= 9 or location < 1:
            raise IHCookerException("location %d must be in [1,8]." % location)
        self.send("set_delete1", [self._device_prefix + "%0d" % location])

    @command(default_output=format_output("Factory reset"))
    def factory_reset(self):
        """Reset device to factory settings, removing menu settings.

        It is unclear if this can change the language setting of the device.
        """

        self.send("set_factory_reset", [self._device_prefix])

    @command(
        click.argument("profile", type=str),
        default_output=format_output(""),
    )
    def profile_to_json(self, profile: Union[str, c.Container, dict]):
        """Convert profile to json."""
        profile = self._prepare_profile(profile)

        res = dict(profile)
        res["menu_settings"] = dict(res["menu_settings"])
        del res["menu_settings"]["_io"]
        del res["_io"]
        del res["crc"]
        res["stages"] = [
            {k: v for k, v in s.items() if k != "_io"} for s in res["stages"]
        ]

        return json.dumps(res)

    @command(
        click.argument("json_str", type=str),
        default_output=format_output(""),
    )
    def json_to_profile(self, json_str: str):
        """Convert json to profile."""

        profile = self._profile_obj.build(self._prepare_profile(json.loads(json_str)))

        return str(profile.hex())

    @command(
        click.argument("value", type=bool),
        default_output=format_output("WiFi led setting changed."),
    )
    def set_wifi_led(self, value: bool):
        """Keep wifi-led on when idle."""
        return self.send(
            "set_wifi_state", [self._device_prefix + "01" if value else "00"]
        )

    @command(
        click.argument("power", type=int),
        default_output=format_output("Fire power set."),
    )
    def set_power(self, power: int):
        """Set fire power."""
        if not 0 <= power < 100:
            raise ValueError("Power should be in range [0,99]")
        return self.send(
            "set_fire", [self._device_prefix + "0005"]
        )  # + f'{power:02x}'])

    @command(
        click.argument("profile", type=str),
        click.argument("location", type=int),
        click.argument("confirm_start", type=bool),
        default_output=format_output("Setting menu."),
    )
    def set_menu(
        self,
        profile: Union[str, c.Container, dict],
        location: int,
        confirm_start=False,
    ):
        """Updates one of the menu options with the profile.

        Args:
        - location, int in range(1, 9)
        - skip_confirmation, if True, request confirmation to start recipe as well.
        """
        profile = self._prepare_profile(profile)
        print(profile)
        if location >= 9 or location < 1:
            raise IHCookerException("location %d must be in [1,8]." % location)
        profile.menu_settings.save_recipe = True
        profile.confirm_start = confirm_start
        profile.menu_location = location

        self.send("set_menu1", [self._profile_obj.build(profile).hex()])

    @property
    def _profile_obj(self) -> c.Struct:
        if self.model in MODEL_VERSION1:
            return profile_v1
        elif self.model == MODEL_KOREA1:
            return profile_korea
        else:
            return profile_v2

    def _prepare_profile(self, profile: Union[str, c.Container, dict]) -> c.Container:
        if isinstance(profile, str):
            if profile.strip().startswith("{"):
                # Assuming JSON string.
                profile = json.loads(profile)
            else:
                profile = self._profile_obj.parse(bytes.fromhex(profile))
        if isinstance(profile, dict):
            for k in profile.keys():
                if k not in profile_keys:
                    raise ValueError("Invalid key %s in profile dict." % k)
            for stage in profile.get("stages", []):
                for i, k in enumerate(stage.keys()):
                    if k not in stage_keys:
                        raise ValueError("Invalid key %s in stage %d." % (k, i))
            for k in profile.get("menu_settings", {}).keys():
                if k not in menu_keys:
                    raise ValueError("Invalid key %s in menu_settings." % (k))

            profile = self._profile_obj.parse(self._profile_obj.build(profile))
        elif isinstance(profile, c.Container):
            pass
        else:
            raise ValueError("Invalid profile object")

        profile.device_version = DEVICE_ID[self.model]
        return profile

    @property
    def _device_prefix(self):
        if self.model not in DEVICE_ID:
            raise IHCookerException(
                "Model %s currently unsupported, please report this on github."
                % self.model
            )

        prefix = "03%02d" % DEVICE_ID.get(self.model, None)
        return prefix
