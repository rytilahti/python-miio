import logging
import enum
from collections import defaultdict
from .device import Device

_LOGGER = logging.getLogger(__name__)

MODEL_PRESS1 = 'chunmi.cooker.press1'
MODEL_PRESS2 = 'chunmi.cooker.press2'
MODEL_NORMAL1 = 'chunmi.cooker.normal1'
MODEL_NORMAL2 = 'chunmi.cooker.normal2'
MODEL_NORMAL4 = 'chunmi.cooker.normal3'
MODEL_NORMAL3 = 'chunmi.cooker.normal4'
MODEL_NORMAL5 = 'chunmi.cooker.normal5'

MODEL_PRESS = [MODEL_PRESS1, MODEL_PRESS2]
MODEL_NORMAL = [MODEL_NORMAL1, MODEL_NORMAL2, MODEL_NORMAL3, MODEL_NORMAL4,
                MODEL_NORMAL5]


class OperationMode(enum.Enum):
    AutoKeepWarm = 'autokeepwarm'
    Cancel = 'Отмена'
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
    Running = 'running'
    Start = 'start'
    StartP = 'startp'
    Waiting = 'waiting'


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
    def setting(self) -> str:
        return self.data['setting']

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
        self.send('set_start', [profile])

    def stop(self):
        self.send('set_func', ['end02'])

    def stop_outdated_firmware(self):
        self.send('set_func', ['end'])

    def set_no_warnings(self):
        self.send('set_func', ['nowarn'])

    def set_acknowledge(self):
        self.send('set_func', ['ack'])

    def set_interaction(self, setting, shut_led_delay, lid_open_timeout,
                        lid_open_timeout_alarm_time):
        """Set interaction. Supported by all cookers except MODEL_PRESS1

        FIXME: Assemble a proper bitmask. All parameters are hex values
        """
        self.send('set_interaction',
                  [setting,
                   shut_led_delay,
                   lid_open_timeout,
                   lid_open_timeout_alarm_time])

    def set_menu(self, profile: str):
        """Add a cooking profile to the menu"""
        self.send('set_menu', [profile])
