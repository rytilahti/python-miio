import json
import warnings
from collections import defaultdict
from typing import Optional, Union

import click
import construct as c

from miio import Device, DeviceStatus
from miio.click_common import command, format_output

from . import (
    DEVICE_ID,
    MODEL_KOREA1,
    MODEL_VERSION1,
    MODEL_VERSION2,
    SUPPORTED_MODELS,
    IHCookerException,
    OperationMode,
    StageMode,
)
from .recipe_profile import (
    DEFAULT_FIRE_LEVEL,
    RECIPE_NAME_MAX_LEN_V1,
    RECIPE_NAME_MAX_LEN_V2,
    menu_keys,
    profile_keys,
    profile_korea,
    profile_v1,
    profile_v2,
    stage_keys,
)


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
        click.argument("menu_location", type=int, default=None),
        default_output=format_output("Cooking with temperature requested."),
    )
    def start_temp(
        self,
        temperature,
        minutes=60,
        power=DEFAULT_FIRE_LEVEL,
        skip_confirmation=False,
        menu_location=None,
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

        if menu_location is not None:
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

        if location >= 9 or location < 0:
            raise IHCookerException("location %d must be in [0,9]." % location)
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
