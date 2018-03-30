import logging
import enum
import string
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


class CookerSettings:
    def __init__(self, settings: int):
        """
        Setting examples: 1407, 0607, 0207
        """
        self.settings = settings

    @property
    def pressure_supported(self) -> bool:
        return (self.settings & 1) != 0

    @property
    def led_on(self) -> bool:
        return (self.settings & 2) != 0

    @property
    def lid_open_alarm(self) -> bool:
        return (self.settings & 8) != 0

    @property
    def lid_open_timeout_alarm(self) -> bool:
        return (self.settings & 16) != 0

    def set_pressure_supported(self, supported: bool):
        if supported:
            self.settings |= 1
        else:
            self.settings &= 254

    def set_led_on(self, on: bool):
        if on:
            self.settings |= 2
        else:
            self.settings &= 253

    def set_lid_open_alarm(self, alarm: bool):
        if alarm:
            self.settings |= 8
        else:
            self.settings &= 247

    def set_lid_open_timeout_alarm(self, alarm: bool):
        if alarm:
            self.settings |= 16
        else:
            self.settings &= 239

    def __str__(self) -> str:
        return str(self.settings).zfill(4)

    def __repr__(self) -> str:
        s = "<CookerSettings pressure_supported=%s, " \
            "led_on=%s, " \
            "lid_open_alarm=%s, " \
            "lid_open_timeout_alarm=%s>" % \
            (self.pressure_supported,
             self.led_on,
             self.lid_open_alarm,
             self.lid_open_timeout_alarm)
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
        """
        self.data = data

    @property
    def mode(self) -> OperationMode:
        """Current operation mode."""
        return OperationMode(self.data['func'])

    @property
    def menu(self) -> str:
        return self.data['menu']

    @property
    def stage(self) -> str:
        """
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
        return self.data['stage']

    @property
    def temperature(self) -> int:
        return int(self.data['temp'])

    @property
    def t_func(self) -> str:
        return self.data['t_func']

    @property
    def t_precook(self) -> str:
        return self.data['t_precook']

    @property
    def cooking_temperature(self) -> str:
        return self.data['temperature_cook']

    @property
    def setting(self) -> CookerSettings:
        return CookerSettings(int(self.data['setting']))

    @property
    def delay(self) -> str:
        return self.data['delay']

    @property
    def version(self) -> str:
        return self.data['version']

    @property
    def favorite(self) -> str:
        return self.data['favorite']

    @property
    def custom(self) -> str:
        return self.data['custom']

    def __repr__(self) -> str:
        s = "<CookerStatus mode=%s " \
            "menu=%s, " \
            "stage=%s, " \
            "temperature=%s, " \
            "t_func=%s, " \
            "t_precook=%s, " \
            "cooking_temperature=%s, " \
            "setting=%s, " \
            "delay=%s, " \
            "version=%s, " \
            "favorite=%s, " \
            "custom=%s>" % \
            (self.mode,
             self.menu,
             self.stage,
             self.temperature,
             self.t_func,
             self.t_precook,
             self.cooking_temperature,
             self.setting,
             self.delay,
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
        """Start cooking a profile"""
        if not self._validate_profile(profile):
            raise CookerException("Invalid cooking profile: %s" % profile)

        self.send('set_start', [profile])

    def stop(self):
        self.send('set_func', ['end02'])

    def stop_outdated_firmware(self):
        self.send('set_func', ['end'])

    def set_no_warnings(self):
        self.send('set_func', ['nowarn'])

    def set_acknowledge(self):
        self.send('set_func', ['ack'])

    def set_interaction(self, settings: CookerSettings,
                        shut_led_delay,
                        lid_open_timeout,
                        lid_open_timeout_alarm_time):
        """Set interaction. Supported by all cookers except MODEL_PRESS1

        FIXME: Assemble a proper bitmask. All parameters are hex values
        """
        self.send('set_interaction',
                  [str(settings),
                   shut_led_delay,
                   lid_open_timeout,
                   lid_open_timeout_alarm_time])

    def set_menu(self, profile: str):
        """Select one of the default(?) cooking profiles"""
        if not self._validate_profile(profile):
            raise CookerException("Invalid cooking profile: %s" % profile)

        self.send('set_menu', [profile])

    @staticmethod
    def _validate_profile(profile):
        return all(c in string.hexdigits for c in profile) and \
               len(profile) in [228, 242]
