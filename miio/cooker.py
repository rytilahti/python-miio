import logging
import enum
import string
from datetime import time
from typing import Optional
from collections import defaultdict
from .device import Device, DeviceException

_LOGGER = logging.getLogger(__name__)

MODEL_PRESSURE1 = 'chunmi.cooker.press1'
MODEL_PRESSURE2 = 'chunmi.cooker.press2'
MODEL_NORMAL1 = 'chunmi.cooker.normal1'
MODEL_NORMAL2 = 'chunmi.cooker.normal2'
MODEL_NORMAL4 = 'chunmi.cooker.normal3'
MODEL_NORMAL3 = 'chunmi.cooker.normal4'
MODEL_NORMAL5 = 'chunmi.cooker.normal5'

MODEL_PRESSURE = [MODEL_PRESSURE1, MODEL_PRESSURE2]
MODEL_NORMAL = [MODEL_NORMAL1, MODEL_NORMAL2, MODEL_NORMAL3, MODEL_NORMAL4,
                MODEL_NORMAL5]

MODEL_NORMAL_GROUP1 = [MODEL_NORMAL2, MODEL_NORMAL5]
MODEL_NRRMAL_GROUP2 = [MODEL_NORMAL3, MODEL_NORMAL4]

COOKING_STAGE_NAME = [
    'Быстрый разогрев',
    'Температура воды',
    'Кипячение',
    'Давление',
    'Тушеный рис',
]

COOKING_STAGE_DESCRIPTION = [
    'Регулировать температуру, давления, для размягчения риса',
    'Длительный нагрев, рис поглощает воду, становится более насыщенным и',
    'сладким',
    'Держите температуру высокой, рис любит равномерное тепло',
    'Высокотемпературный пар, рис кристально чистый, запечатанный и сладкий',
    'Подогрев риса, раскроет весь его вкус',
]


class CookerException(DeviceException):
    pass


class OperationMode(enum.Enum):
    # Observed
    Running = 'running'
    Waiting = 'waiting'
    AutoKeepWarm = 'autokeepwarm'
    # Potential candidates
    Cooking = 'cooking'
    Finish = 'finish'
    FinishA = 'finisha'
    KeepWarm = 'keepwarm'
    KeepTemp = 'keep_temp'
    Notice = 'notice'
    Offline = 'offline'
    Online = 'online'
    PreCook = 'precook'
    Resume = 'resume'
    ResumeP = 'resumep'
    Start = 'start'
    StartP = 'startp'
    Cancel = 'Отмена'


class CookerCustomizations:
    def __init__(self, custom: str):
        """
        Example values:

        ffffffffffff011effff010000001d1f,
        ffffffffffff011effff010004026460,
        ffffffffffff011effff01000a015559,
        ffffffffffff011effff01000000535d
        """
        self.custom = [int(custom[i:i + 2], 16) for i in
                       range(0, len(custom), 2)]

    @property
    def jingzhu_appointment(self) -> time:
        return time(hour=self.custom[0], minute=self.custom[1])

    @property
    def kuaizhu_appointment(self) -> time:
        return time(hour=self.custom[2], minute=self.custom[3])

    @property
    def zhuzhou_appointment(self) -> time:
        return time(hour=self.custom[4], minute=self.custom[5])

    @property
    def zhuzhou_cooking(self) -> time:
        return time(hour=self.custom[6], minute=self.custom[7])

    @property
    def favorite_appointment(self) -> time:
        return time(hour=self.custom[8], minute=self.custom[9])

    @property
    def favorite_cooking(self) -> time:
        return time(hour=self.custom[10], minute=self.custom[11])

    def __str__(self) -> str:
        return "".join(["{:02x}".format(value) for value in self.custom])

    def __repr__(self) -> str:
        s = "<CookerCustomizations jingzhu_appointment=%s, " \
            "kuaizhu_appointment=%s, " \
            "zhuzhou_appointment=%s, " \
            "zhuzhou_cooking=%s, " \
            "favorite_appointment=%s," \
            "favorite_cooking=%s>" % \
            (self.jingzhu_appointment,
             self.kuaizhu_appointment,
             self.zhuzhou_appointment,
             self.zhuzhou_cooking,
             self.favorite_appointment,
             self.favorite_cooking)
        return s


class CookingStage:
    def __init__(self, stage: str):
        """
        Example timeouts: 'null', 02000000ff, 03000000ff, 0a000000ff, 1000000000

        The meaning of stage[8:10] is unknown.
        """
        self.stage = stage

    @property
    def state(self) -> int:
        """

        10: Cooking finished
        11: Cooking finished
        12: Cooking finished
        """
        return int(self.stage[0:2], 16)

    @property
    def rice_id(self) -> int:
        return int(self.stage[2:6], 16)

    @property
    def taste(self) -> int:
        return int(self.stage[6:8], 16)

    @property
    def taste_phase(self) -> int:
        phase = self.taste / 33

        if phase > 2:
            return 2

    @property
    def name(self) -> str:
        try:
            return COOKING_STAGE_NAME[self.state]
        except IndexError:
            return 'Cooking finished'

    @property
    def description(self) -> str:
        try:
            return COOKING_STAGE_DESCRIPTION[self.state]
        except IndexError:
            return ''

    def __str__(self) -> str:
        return self.stage

    def __repr__(self) -> str:
        s = "<CookingStage state=%s, " \
            "rice_id=%s, " \
            "taste=%s, " \
            "taste_phase=%s, " \
            "raw=%s>" % \
            (self.state,
             self.rice_id,
             self.taste,
             self.taste_phase,
             self.stage)
        return s


class InteractionTimeouts:
    def __init__(self, timeouts: str = None):
        """
        Example timeouts: 05040f, 05060f
        """
        if timeouts is None:
            self.timeouts = [5, 4, 15]
        else:
            self.timeouts = [int(timeouts[i:i + 2], 16) for i in
                             range(0, len(timeouts), 2)]

    @property
    def led_off(self) -> int:
        return self.timeouts[0]

    @property
    def lid_open(self) -> int:
        return self.timeouts[1]

    @property
    def lid_open_warning(self) -> int:
        return self.timeouts[2]

    @led_off.setter
    def led_off(self, delay: int):
        self.timeouts[0] = delay

    @lid_open.setter
    def lid_open(self, timeout: int):
        self.timeouts[1] = timeout

    @lid_open_warning.setter
    def lid_open_warning(self, timeout: int):
        self.timeouts[2] = timeout

    def __str__(self) -> str:
        return "".join(["{:02x}".format(value) for value in self.timeouts])

    def __repr__(self) -> str:
        s = "<InteractionTimeouts led_off=%s, " \
            "lid_open=%s, " \
            "lid_open_warning=%s>" % \
            (self.led_off,
             self.lid_open,
             self.lid_open_warning)
        return s


class CookerSettings:
    def __init__(self, settings: str = None):
        """
        Example settings: 1407, 0607, 0207
        """
        if settings is None:
            self.settings = [0, 4]
        else:
            self.settings = [int(settings[i:i + 2], 16) for i in
                             range(0, len(settings), 2)]

    @property
    def pressure_supported(self) -> bool:
        return self.settings[0] & 1 != 0

    @property
    def led_on(self) -> bool:
        return self.settings[0] & 2 != 0

    @property
    def auto_keep_warm(self) -> bool:
        return self.settings[0] & 4 != 0

    @property
    def lid_open_warning(self) -> bool:
        return self.settings[0] & 8 != 0

    @property
    def lid_open_warning_delayed(self) -> bool:
        return self.settings[0] & 16 != 0

    @property
    def jingzhu_auto_keep_warm(self) -> bool:
        return self.settings[1] & 1 != 0

    @property
    def kuaizhu_auto_keep_warm(self) -> bool:
        return self.settings[1] & 2 != 0

    @property
    def zhuzhou_auto_keep_warm(self) -> bool:
        return self.settings[1] & 4 != 0

    @property
    def favorite_auto_keep_warm(self) -> bool:
        return self.settings[1] & 8 != 0

    @pressure_supported.setter
    def pressure_supported(self, supported: bool):
        if supported:
            self.settings[0] |= 1
        else:
            self.settings[0] &= 254

    @led_on.setter
    def led_on(self, on: bool):
        if on:
            self.settings[0] |= 2
        else:
            self.settings[0] &= 253

    @auto_keep_warm.setter
    def auto_keep_warm(self, keep_warm: bool):
        if keep_warm:
            self.settings[0] |= 4
        else:
            self.settings[0] &= 251

    @lid_open_warning.setter
    def lid_open_warning(self, alarm: bool):
        if alarm:
            self.settings[0] |= 8
        else:
            self.settings[0] &= 247

    @lid_open_warning_delayed.setter
    def lid_open_warning_delayed(self, alarm: bool):
        if alarm:
            self.settings[0] |= 16
        else:
            self.settings[0] &= 239

    @jingzhu_auto_keep_warm.setter
    def jingzhu_auto_keep_warm(self, auto_keep_warm: bool):
        if auto_keep_warm:
            self.settings[1] |= 1
        else:
            self.settings[1] &= 254

    @kuaizhu_auto_keep_warm.setter
    def kuaizhu_auto_keep_warm(self, auto_keep_warm: bool):
        if auto_keep_warm:
            self.settings[1] |= 2
        else:
            self.settings[1] &= 253

    @zhuzhou_auto_keep_warm.setter
    def zhuzhou_auto_keep_warm(self, auto_keep_warm: bool):
        if auto_keep_warm:
            self.settings[1] |= 4
        else:
            self.settings[1] &= 251

    @favorite_auto_keep_warm.setter
    def favorite_auto_keep_warm(self, auto_keep_warm: bool):
        if auto_keep_warm:
            self.settings[1] |= 8
        else:
            self.settings[1] &= 247

    def __str__(self) -> str:
        return "".join(["{:02x}".format(value) for value in self.settings])

    def __repr__(self) -> str:
        s = "<CookerSettings pressure_supported=%s, " \
            "led_on=%s, " \
            "lid_open_warning=%s, " \
            "lid_open_warning_delayed=%s, " \
            "auto_keep_warm=%s, " \
            "jingzhu_auto_keep_warm=%s, " \
            "kuaizhu_auto_keep_warm=%s, " \
            "zhuzhou_auto_keep_warm=%s, " \
            "favorite_auto_keep_warm=%s>" % \
            (self.pressure_supported,
             self.led_on,
             self.lid_open_warning,
             self.lid_open_warning_delayed,
             self.auto_keep_warm,
             self.jingzhu_auto_keep_warm,
             self.kuaizhu_auto_keep_warm,
             self.zhuzhou_auto_keep_warm,
             self.favorite_auto_keep_warm)
        return s


class CookerStatus:
    def __init__(self, data):
        """
        Responses of a chunmi.cooker.normal2 (fw_ver: 1.2.8):

        { 'func': 'precook',
          'menu': '0001',
          'stage': '009ce63cff',
          'temp': 21,
          't_func': '769',
          't_precook': '1180',
          't_cook': 60,
          'setting': '1407',
          'delay': '05060f',
          'version': '00030017',
          'favorite': '0100',
          'custom': '13281323ffff011effff010000001516'}
        { 'func': 'waiting',
          'menu': '0001',
          'stage': 'null',
          'temp': 22,
          't_func': 60,
          't_precook': -1,
          't_cook': 60,
          'setting': '1407',
          'delay': '05060f',
          'version': '00030017',
          'favorite': '0100',
          'custom': '13281323ffff011effff010000001617'}

                                              func   ,       menu ,    stage    ,    temp   ,   t_func, t_precook, t_cook, setting,   delay ,  version  , favorite,               custom
        idle:                              ['waiting',      '0001', 'null',             '29',     '60',      '-1',   '60',  '0607', '05040f', '00030017',   '0100', 'ffffffffffff011effff010000001d1f']
        quickly preheat:                   ['running',      '0001', '00000000ff', '031e0b23',     '60',      '-1',   '60',  '0607', '05040f', '00030017',   '0100', 'ffffffffffff011effff010000001d1f']
        absorb water at moderate temp:     ['running',      '0001', '02000000ff', '031e0b23',     '54',      '-1',   '60',  '0607', '05040f', '00030017',   '0100', 'ffffffffffff011effff010002013e23']
        absorb water at moderate temp:     ['running',      '0001', '02000000ff', '031e0b23',     '48',      '-1',   '60',  '0607', '05040f', '00030017',   '0100', 'ffffffffffff011effff010002013f29']
        operate at full load to boil rice: ['running',      '0001', '03000000ff', '031e0b23',     '39',      '-1',   '60',  '0607', '05040f', '00030017',   '0100', 'ffffffffffff011effff010003055332']
        operate at full load to boil rice: ['running',      '0001', '04000000ff', '031e0b23',     '35',      '-1',   '60',  '0607', '05040f', '00030017',   '0100', 'ffffffffffff011effff010004026460']
        operate at full load to boil rice: ['running',      '0001', '06000000ff', '031e0b23',     '29',      '-1',   '60',  '0607', '05040f', '00030017',   '0100', 'ffffffffffff011effff010006015c64']
        high temperature gelatinization:   ['running',      '0001', '07000000ff', '031e0b23',     '22',      '-1',   '60',  '0607', '05040f', '00030017',   '0100', 'ffffffffffff011effff010007015d64']
        temperature gelatinization:        ['running',      '0001', '0a000000ff', '031e0b23',     '2',       '-1',   '60',  '0607', '05040f', '00030017',   '0100', 'ffffffffffff011effff01000a015559']
        meal is ready:                     ['autokeepwarm', '0001', '1000000000', '031e0b23031e', '1',      '750',   '60',  '0207', '05040f', '00030017',   '0100', 'ffffffffffff011effff01000000535d']
        """
        self.data = data

    @property
    def mode(self) -> OperationMode:
        """Current operation mode."""
        return OperationMode(self.data['func'])

    @property
    def menu(self) -> int:
        """Selected recipe id."""
        return int(self.data['menu'], 16)

    @property
    def stage(self) -> Optional[CookingStage]:
        """Current stage if cooking."""
        stage = self.data['stage']
        if len(stage) == 10 and stage.hexdigits:
            return CookingStage(stage)

        return None

    @property
    def temperature(self) -> Optional[int]:
        """
        Current temperature, if idle.

        Example values: *29*, 031e0b23, 031e0b23031e
        """
        value = self.data['temp']
        if len(value) == 2 and value.isdigit():
            return int(value)

        return None

    @property
    def start_time(self) -> Optional[time]:
        """
        Start time of cooking?

        The property "temp" is used for different purposes.
        Example values: 29, *031e0b23*, 031e0b23031e
        """
        value = self.data['temp']
        if len(value) == 8 and value.hexdigits:
            return time(hour=int(value[4:6], 16), minute=int(value[6:8], 16))

        return None

    @property
    def remaining(self) -> int:
        """Remaining minutes of the cooking process."""
        return int(self.data['t_func'])

    @property
    def cooking_delayed(self) -> Optional[int]:
        """Wait n minutes before cooking / scheduled cooking."""
        delay = int(self.data['t_precook'])

        if delay >= 0:
            return delay

        return None

    @property
    def duration(self) -> int:
        """Duration of the cooking process."""
        return int(self.data['t_cook'])

    @property
    def settings(self) -> CookerSettings:
        """Settings of the cooker."""
        return CookerSettings(self.data['setting'])

    @property
    def interaction_timeouts(self) -> InteractionTimeouts:
        """Interaction timeouts."""
        return InteractionTimeouts(self.data['delay'])

    @property
    def hardware_version(self) -> int:
        """Hardware version."""
        return int(self.data['version'][0:4], 16)

    @property
    def firmware_version(self) -> int:
        """Firmware version."""
        return int(self.data['version'][4:8], 16)

    @property
    def favorite(self) -> int:
        """Favored recipe id. Can be compared with the menu property."""
        return int(self.data['favorite'], 16)

    @property
    def custom(self) -> Optional[CookerCustomizations]:
        custom = self.data['custom']

        if len(custom) > 31 and custom.hexdigits:
            return CookerCustomizations(custom)

        return None

    def __repr__(self) -> str:
        s = "<CookerStatus mode=%s " \
            "menu=%s, " \
            "stage=%s, " \
            "temperature=%s, " \
            "remaining=%s, " \
            "cooking_delayed=%s, " \
            "cooking_temperature=%s, " \
            "settings=%s, " \
            "interaction_timeouts=%s, " \
            "version=%s, " \
            "favorite=%s, " \
            "custom=%s>" % \
            (self.mode,
             self.menu,
             self.stage,
             self.temperature,
             self.remaining,
             self.cooking_delayed,
             self.duration,
             self.settings,
             self.interaction_timeouts,
             self.version,
             self.favorite,
             self.custom)
        return s


class Cooker(Device):
    """Main class representing the cooker."""

    def status(self) -> CookerStatus:
        """Retrieve properties."""
        properties = ['func', 'menu', 'stage', 'temp', 't_func', 't_precook',
                      't_cook', 'setting', 'delay', 'version']
        values = self.send("get_prop", properties)

        properties_count = len(properties)
        values_count = len(values)
        if properties_count != values_count:
            _LOGGER.debug(
                "Count (%s) of requested properties does not match the "
                "count (%s) of received values.",
                properties_count, values_count)

        return CookerStatus(
            defaultdict(lambda: None, zip(properties, values)))

    def start(self, profile: str):
        """Start cooking a profile."""
        if not self._validate_profile(profile):
            raise CookerException("Invalid cooking profile: %s" % profile)

        self.send('set_start', [profile])

    def stop(self):
        """Stop cooking."""
        self.send('set_func', ['end02'])

    def stop_outdated_firmware(self):
        """Stop cooking (obsolete)."""
        self.send('set_func', ['end'])

    def set_no_warnings(self):
        """Disable warnings."""
        self.send('set_func', ['nowarn'])

    def set_acknowledge(self):
        """Enable warnings?"""
        self.send('set_func', ['ack'])

    def set_interaction(self, settings: CookerSettings,
                        timeouts: InteractionTimeouts):
        """Set interaction. Supported by all cookers except MODEL_PRESS1"""
        self.send('set_interaction',
                  [str(settings),
                   "{:x}".format(timeouts.led_off),
                   "{:x}".format(timeouts.lid_open),
                   "{:x}".format(timeouts.lid_open_warning)])

    def set_menu(self, profile: str):
        """Select one of the default(?) cooking profiles"""
        if not self._validate_profile(profile):
            raise CookerException("Invalid cooking profile: %s" % profile)

        self.send('set_menu', [profile])

    @staticmethod
    def _validate_profile(profile):
        return all(c in string.hexdigits for c in profile) and \
               len(profile) in [228, 242]
