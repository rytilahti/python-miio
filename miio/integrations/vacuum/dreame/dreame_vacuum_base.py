from miio.device import Device
import logging
import time
from enum import Enum
logger = logging.getLogger(__name__)

class ChargingState(Enum):
    Unknown = -1
    Charging = 1
    Discharging = 2
    Charging2 = 4
    GoCharging = 5

class CleaningMode(Enum):
    Unknown = -1
    Quiet = 0
    Default = 1
    Medium = 2
    Strong = 3

class OperatingMode(Enum):
    Unknown = -1
    Paused = 1
    Cleaning = 2
    GoCharging = 3
    Charging = 6
    ManualCleaning = 13
    Sleeping = 14
    ManualPaused = 17
    ZonedCleaning = 19

class FaultStatus(Enum):
    Unknown = -1
    NoFaults = 0

class DeviceStatus(Enum):
    Unknown = -1
    Sweeping = 1
    Idle = 2
    Paused = 3
    Error = 4
    GoCharging = 5
    Charging = 6
    ManualSweeping = 13

class MopMode(Enum):
    Unknown = -1
    Low = 1
    Mid = 2
    High = 3

class WarningCode(Enum):
    Unknown = -1
    Normal = 0
    Drop = 1
    Cliff = 2
    Bumper = 3
    Gesture = 4
    BumperRepeat = 5
    DropRepeat = 6
    OpticalFlow = 7
    NoBox = 8
    NoTankbox = 9
    WaterboxEmpty = 10
    BoxFull = 11
    Brush = 12
    SideBrush = 13
    Fan = 14
    LeftWheelMotor = 15
    RightWheelMotor = 16
    TurnSuffocate = 17
    ForwardSuffocate = 18
    ChargerGet = 19
    BatteryLow = 20
    ChargeFault = 21
    BatteryPercentage = 22
    Heart = 23
    CameraOcclusion = 24
    CameraFault = 25
    EventBattery = 26
    ForwardLooking = 27
    Gyroscope = 28

def percent_format(val):
    return f'{val}%'

def minutes_format(val):
    return f'{val}min ({val/60:.3f}h / {val/60/24:.3f} days)'

def hours_format(val):
    return f'{val}h ({val/24:.3f} days)'

def epoch_time_format(val):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(val))

class DreameVacuumBase(Device):
    def get_properties(self, *prop):
        if len(prop) > 20:
            raise Exception(f'number of properties cannot exceed 20. {len(prop)} found.')
        prop_list = []
        for p in prop:
            ppar = self.commands[p]
            if 'r' in ppar['mode']:
                prop_list.append({'did': p, 'siid': ppar['siid'], 'piid': ppar['piid']})
            else:
                logger.warning(f'{p} has no read mode')
        res = self.send('get_properties', prop_list)
        for r in res:
            if 'value' in r:
                r['decoded'] = self.commands[r['did']]['mode']['r'](r['value'])
            else:
                r['decoded'] = 'N/A'
        return res

    def set_prop_str(self, par, val):
        ppar = self.commands[par]
        if 'w' in ppar['mode']:
            return {'did': par, 'siid': ppar['siid'], 'piid': ppar['piid'], 'value': ppar['mode']['w'](val)}
        else:
            logger.warning(f'{par} has no write mode')
            return None

    def set_properties(self, **kwargs):
        prop_list = [self.set_prop_str(p, v) for p, v in kwargs.items()]
        res = self.send('set_properties', prop_list)
        return res

    def action(self, act, **pars):
        pars_list = []
        apar = self.commands[act]
        if 'a' in apar['mode']:
            for p, val in pars.items():
                par_dic = self.set_prop_str(p, val)
                pars_list.append({'piid': par_dic['piid'], 'value': par_dic['value']})
            act_dic = {'did': act, 'siid': apar['siid'], 'aiid': apar['aiid'], 'in': pars_list}
            return self.send('action', act_dic)
        else:
            logger.warning(f'{act} has no command mode')
            return None
