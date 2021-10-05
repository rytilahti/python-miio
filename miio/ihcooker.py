import codecs
import enum
import logging
import random
import warnings
import crc16
from collections import defaultdict
from typing import Dict, List, Optional, Union

import click

from .click_common import command, format_output
from .device import Device
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
DEVICE_ID = {
    MODEL_EG1: 2,  # TODO: TBD
    MODEL_EXP1: 4,
    MODEL_FW: 1,  # TODO: TBD
    MODEL_HK1: 1,  # TODO: TBD
    MODEL_KOREA1: 2,  # TODO: TBD
    MODEL_TW1: 1,  # TODO: TBD
    MODEL_V1: 1,
}
DEVICE_PREFIX = {k: "03%02d" % v for k, v in DEVICE_ID.items()}

VERSION_1 = 1
VERSION_2 = 2

OFFSET_MYSTERY_BIT_V1 = 30
OFFSET_MYSTERY_BIT_V2 = 46

OFFSET_DURATION_MIN_V1 = 26
OFFSET_DURATION_MIN_V2 = 42
OFFSET_DURATION_MAX_V1 = 24
OFFSET_DURATION_MAX_V2 = 40

OFFSET_DURATION_V1 = 38
OFFSET_DURATION_V2 = 22

OFFSET_RECIPE_ID_V1 = 17
OFFSET_RECIPE_ID_V2 = 33

RECIPE_NAME_MAX_LEN_V1 = 13
RECIPE_NAME_MAX_LEN_V2 = 28

OFFSET_SET_START_V1 = 21
OFFSET_SET_START_V2 = 37

OFFSET_PHASE_V1 = 38
OFFSET_PHASE_V2 = 48

MAX_RECIPE_NAME_V1 = 28
MAX_RECIPE_NAME_V2 = 58

OFFSET_RECIPE_NAME = 3

DEFAULT_FIRE_ON_OFF = 20

DEFAULT_THRESHOLD_CELCIUS = 249
DEFAULT_TEMP_TARGET_CELCIUS = 229

DEFAULT_FIRE_LEVEL = 45

DEFAULT_PHASE_MINUTES = 45


class IHCookerException(DeviceException):
    pass


class StageMode(enum.Enum):
    FireMode = 0
    TemperatureMode = 2
    Unknown1 = 4
    TempAutoSmallPot = 8
    TempAutoBigPot = 24
    Unknown2 = 16


class OperationMode(enum.Enum):
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


class CookProfile:
    def __init__(self, model, profile=None):
        self.model = model
        """Initialize a cooking profile from an existing one, or a new one."""
        if profile is not None:
            self.data = bytearray.fromhex(profile)
        else:
            self.data = bytearray([0] * 179)
            # Initialize recipe phases.
            if self.is_v1:
                offset = OFFSET_PHASE_V1
            else:
                offset = OFFSET_PHASE_V2

            for i in range(offset, 15 * 8, 8):
                self.data[i + 0] = 0
                self.data[i + 1] = 0
                self.data[i + 2] = 0
                self.data[i + 3] = DEFAULT_THRESHOLD_CELCIUS
                self.data[i + 4] = DEFAULT_TEMP_TARGET_CELCIUS
                self.data[i + 5] = 0
                self.data[i + 6] = DEFAULT_FIRE_ON_OFF
                self.data[i + 7] = DEFAULT_FIRE_ON_OFF
            recipe_id = random.randint(0, 2 ** 32 - 1)
            self.set_recipe_id(recipe_id)
            self.set_recipe_name("Custom %d" % recipe_id)
            self.set_duration(60)

    @property
    def is_v1(self):
        return self.model in MODEL_VERSION1

    @property
    def is_v2(self):
        return self.model in MODEL_VERSION2

    def set_start_remind(self, value):
        """Prompt user to start recipe, used with set_menu function."""
        if self.is_v1:
            i = OFFSET_SET_START_V1
        else:
            i = OFFSET_SET_START_V2
        if value:
            self.data[i] = self.data[i] | 64
        else:
            self.data[i] = self.data[i] & 190

    def set_sequence(self, location=9):
        """Favorite location. set to 9 to not save, just request confirmation with set_start_remind."""
        self.data[2] = location & 255

    def set_recipe_name(self, name):
        if name is None:
            name = ""
        name = name.replace(" ", "\n")
        name_b = codecs.encode(name, "ascii")
        if self.is_v1:
            max_len = RECIPE_NAME_MAX_LEN_V1
        else:
            max_len = RECIPE_NAME_MAX_LEN_V2
        for i in range(max_len):
            if i < len(name_b):
                print(name_b[i])
                self.data[i + OFFSET_RECIPE_NAME] = name_b[i]
            else:
                self.data[i + OFFSET_RECIPE_NAME] = 0

    def set_recipe_phases(self, phases: List[Dict[str, int]]):
        """Set up to 16 phases of this recipe.
        Phases are encoded using a 8 numbers:
        mode, 128+hours, minutes, temp_threshold, temp_target, fire_power, 20 (unknown), 20 (unknown)
        The last two numbers' purpose is unclear, but appear to be 20, 20 in almost all recipes.

        Args:
        - phases is a list of up to 16 dicts representing each phase.
            A phase is consists of the following options:
            {
                mode: StageMode.
                temp: target temperature to heat to, in celsius.
                thresh: temperature threshold for moving to next phase, in celcius.
                mins: how long this phase lasts in minutes.
                fire: power output between [0,99]
                fire_on: [0,20] (untested)
                fire_off: [0,20] (untested)
            }
        """
        if self.is_v1:
            offset = OFFSET_PHASE_V1
        else:
            offset = OFFSET_PHASE_V2
        temp_target = DEFAULT_TEMP_TARGET_CELCIUS
        for phase_i in range(15):
            o = offset + phase_i * 8
            if phase_i >= len(phases):
                self.data[o + 0] = 0
                self.data[o + 1] = 0
                self.data[o + 2] = 0
                self.data[o + 3] = DEFAULT_THRESHOLD_CELCIUS
                self.data[o + 4] = temp_target
                self.data[o + 5] = 0
                self.data[o + 6] = DEFAULT_FIRE_ON_OFF
                self.data[o + 7] = DEFAULT_FIRE_ON_OFF
            else:
                # self.data[0] is the mode. There are 6 bits to set for the flag. I've only seen 2, 8, and 26 set.
                phase = phases[phase_i]
                temp_target = phase.get("temp", 0)
                temp_threshold = phase.get("thresh", DEFAULT_THRESHOLD_CELCIUS)
                mode = phase.get("mode", StageMode.FireMode)
                fire = phase.get("fire", DEFAULT_FIRE_LEVEL)
                minutes = phase.get("mins", DEFAULT_PHASE_MINUTES)
                hours = minutes // 60
                minutes = minutes % 60
                fire_on = phase.get("fire_on", DEFAULT_FIRE_ON_OFF)  # values [0-20].
                fire_off = phase.get("fire_off", DEFAULT_FIRE_ON_OFF)  # values [0-20].

                self.data[o + 0] = mode
                self.data[o + 1] = 128 + hours
                self.data[o + 2] = minutes
                self.data[o + 3] = temp_threshold
                self.data[o + 4] = temp_target
                self.data[o + 5] = fire
                self.data[o + 6] = fire_off  # there is one recipe where these bits are set.
                self.data[o + 7] = fire_on

    def set_save_recipe(self, save: bool):
        """Flag if recipe should be stored in menu"""
        if self.is_v1:
            i = OFFSET_SET_START_V1
        else:
            i = OFFSET_SET_START_V2
        if save:
            self.data[i] = self.data[i] | 0
        else:
            self.data[i] = self.data[i] & 255

    def set_recipe_id(self, j: int):
        """Set recipe identifier"""
        if self.is_v1:
            i = OFFSET_RECIPE_ID_V1
        else:
            i = OFFSET_RECIPE_ID_V2
        self.data[i + 0] = (j >> 24) & 255
        self.data[i + 1] = (j >> 16) & 255
        self.data[i + 2] = (j >> 8) & 255
        self.data[i + 3] = j & 255

    def set_duration(self, minutes):
        """Sets global timer for recipe. Runs independently from recipe phase timers."""
        hours = minutes // 60
        mins = minutes % 60
        if self.is_v1:
            i = OFFSET_DURATION_V1
        else:
            i = OFFSET_DURATION_V2
        self.data[i] = hours
        self.data[i + 1] = mins

    def set_duration_minimum(self, minutes):
        """Sets what appears to be the minimum time for recipe. Usage unknown."""
        hours = minutes // 60
        mins = minutes % 60
        if self.is_v1:
            i = OFFSET_DURATION_MIN_V1
        else:
            i = OFFSET_DURATION_MIN_V2
        self.data[i] = hours
        self.data[i + 1] = mins

    def set_duration_maximum(self, minutes):
        """Sets what appears to be the maximum time for recipe. Usage unknown."""
        hours = minutes // 60
        mins = minutes % 60
        if self.is_v1:
            i = OFFSET_DURATION_MAX_V1
        else:
            i = OFFSET_DURATION_MAX_V2
        self.data[i] = hours
        self.data[i + 1] = mins

    def to_hex(self):
        self.data[0] = 3
        self.data[1] = DEVICE_ID[self.model]
        if self.is_v1:
            mystery_bit_i = OFFSET_MYSTERY_BIT_V1
        else:
            mystery_bit_i = OFFSET_MYSTERY_BIT_V2
        self.data[mystery_bit_i] = 1  # This bit is always set

        crc = crc16.crc16xmodem(bytes(self.data[0:-2]))

        self.data[-2] = (crc >> 8) & 255
        self.data[-1] = crc & 255

        return codecs.encode(self.data, "hex").decode("ascii")


class IHCookerStatus:
    def __init__(self, model, data):
        """
        Responses of a chunmi.ihcooker.exp1 (fw_ver: 1.3.6.0013):

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
        name = bytes.fromhex(self.data["menu"][2:cap]).decode("ascii").strip("\x00")
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
        """
        Current temperature, if idle.
        """
        if not self.is_error:
            action = self.data["action"]
            if len(action) >= 6:
                return int.from_bytes(bytes.fromhex(action[2:4]), "little")
        return None

    @property
    def fire_selected(self) -> Optional[int]:
        """Selected power/fire level, differs from current acting power/fire level which auto-adjusts,
        see fire_current.
        """
        if not self.is_error:
            action = self.data["action"]
            if len(action) >= 6:
                return int.from_bytes(bytes.fromhex(action[4:6]), "little")
        return None

    @property
    def stage_mode(self) -> Optional[int]:
        """Bit flags for current cooking stage.
        Current understanding:
        0: constant power output.
        2: Temperature control.
        4: Unknown.
        8: Temp regulation and fire hard coded for small pot @coolibry
        16: Unknown.
        24: Temp regulation and fire hard coded for big pot @coolibry
        """
        # TODO: parse as separate properties when stage figured out.
        if not self.is_error:
            action = self.data["action"]
            if len(action) >= 8:
                return int.from_bytes(bytes.fromhex(action[6:8]), "little")
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
        """Phase from play field"""
        if not self.is_error:
            play = self.data["play"]
            if len(play) == 18:
                return int.from_bytes(bytes.fromhex(play[0:2]), "little")
        return None

    @property
    def play_unknown_2(self) -> Optional[int]:
        """Second value from play field, remains 0, usage unknown"""
        if not self.is_error:
            play = self.data["play"]
            if len(play) == 18:
                return int.from_bytes(bytes.fromhex(play[2:4]), "little")
        return None

    @property
    def play_unknown_3(self) -> Optional[int]:
        """Third value from play field, usage unknown
        Fluctuates apparently randomly between [225, 226, 228, 229, 230, 231, 233, 234, 235]"""
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
        """Matches fire value of action field"""
        if not self.is_error:
            play = self.data["play"]
            if len(play) == 18:
                return int.from_bytes(bytes.fromhex(play[8:10]), "little")
        return None

    @property
    def play_temperature(self) -> Optional[int]:
        """Matches measured temperature value of action field"""
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
        """Ninth value from play field, remains zero, usage unknown"""
        if not self.is_error:
            play = self.data["play"]
            if len(play) == 18:
                return int.from_bytes(bytes.fromhex(play[16:18]), "little")
        return None

    # TODO: Fully parse timer field.
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

    def __repr__(self) -> str:
        s = (
                "<CookerStatus mode=%s "
                "menu=%s, "
                "stage=%s, "
                "temperature=%s, "
                # "start_time=%s"
                # "remaining=%s, "
                # "cooking_delayed=%s, "
                "target_temperature=%s, "
                "wifi_led_setting=%s, "
                "hardware_version=%s, "
                "firmware_version=%s>"
                % (
                    self.mode,
                    self.recipe_name,
                    self.stage,
                    self.temperature,
                    self.target_temp,
                    # self.start_time,
                    # self.remaining,
                    # self.cooking_delayed,
                    self.wifi_led_setting,
                    self.hardware_version,
                    self.firmware_version,
                )
        )
        return s


class IHCooker(Device):
    """Main class representing the induction cooker.

    Custom recipes can be build with the CookProfile class."""

    def __init__(
            self,
            ip: str = None,
            token: str = None,
            start_id: int = 0,
            debug: int = 0,
            lazy_discover: bool = True,
    ) -> None:
        super().__init__(ip, token, start_id, debug, lazy_discover)
        self._model = None

    @command(
        # TODO: update these below.
        default_output=format_output(
            "",
            "Mode: {result.mode}\n"
            "Menu: {result.menu}\n"
            "Temperature: {result.temperature}\n"
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
        click.argument("skip_confirmation", type=bool),
        default_output=format_output("Cooking profile started"),
    )
    def start(self, profile: str, skip_confirmation=False):
        """Start cooking a profile.

        Please do not use skip_confirmation=True, as this is potentially unsafe."""

        profile = self._prepare_profile(profile)
        profile.set_save_recipe(False)
        profile.set_sequence(9)
        if skip_confirmation:
            warnings.warn(
                "You're starting a profile without confirmation, which is a potentially unsafe."
            )
            self.send("set_start", [profile.to_hex()])
        else:
            profile.set_start_remind(True)
            self.send("set_menu1", [profile.to_hex()])

    @command(default_output=format_output("Cooking stopped"))
    def stop(self):
        """Stop cooking."""
        self.send("set_func", ["end"])

    @command(default_output=format_output("Cooking stopped"))
    def stop(self, location):
        """Delete recipe at location [0,7]"""
        if location >= 8 or location < 0:
            raise IHCookerException("location %d must be in [0,7]." % location)
        self.send("set_delete1", [self.device_prefix + "%0d" % location])

    @command(default_output=format_output("Factory reset"))
    def factory_reset(self):
        """Reset device to factory settings, removing menu settings.
        It is unclear if this can change the language setting of the device."""

        self.send("set_factory_reset", [self.device_prefix])

    @command(default_output=format_output("WiFi led setting changed."))
    def set_wifi_led(self, value: bool):
        """Keep wifi-led on when idle."""
        return self.send(
            "set_wifi_state", [self.device_prefix + "01" if value else "00"]
        )

    @command(
        click.argument("profile", type=str),
        default_output=format_output("Setting menu to {profile}"),
    )
    def set_menu(
            self, profile: Union[str, CookProfile], location: int, confirm_start=False
    ):
        """Updates one of the menu options with the profile.

        Args:
        - location, int in range(8)
        - confirm_start, if True, request confirmation to start recipe as well."""
        profile = self._prepare_profile(profile)
        if location >= 8 or location < 0:
            raise IHCookerException("location %d must be in [0,7]." % location)
        profile.set_save_recipe(True)
        profile.set_sequence(location)
        profile.set_start_remind(confirm_start)

        self.send("set_menu1", [profile.to_hex()])

    def _prepare_profile(self, profile):
        if isinstance(profile, str):
            profile = CookProfile(self.model, profile)
        return profile

    @property
    def model(self):
        if self._model is None:
            self._model = self.info().model
        return self._model

    @property
    def device_prefix(self):
        prefix = DEVICE_PREFIX.get(self.model, None)
        if prefix is None:
            raise IHCookerException(
                "Model %s currently unsupported, please report this on github."
                % self.model
            )
        return prefix
