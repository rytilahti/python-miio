# flake8: noqa
try:
    # python 3.7 and earlier
    from importlib_metadata import version  # type: ignore
except ImportError:
    # python 3.8 and later
    from importlib.metadata import version  # type: ignore

# Library imports need to be on top to avoid problems with
# circular dependencies. As these do not change that often
# they can be marked to be skipped for isort runs.
from miio.device import Device, DeviceStatus  # isort: skip
from miio.exceptions import DeviceError, DeviceException  # isort: skip
from miio.miot_device import MiotDevice  # isort: skip

# Integration imports
from miio.airconditioner_miot import AirConditionerMiot
from miio.airconditioningcompanion import (
    AirConditioningCompanion,
    AirConditioningCompanionV3,
)
from miio.airconditioningcompanionMCN import AirConditioningCompanionMcn02
from miio.airdehumidifier import AirDehumidifier
from miio.airfresh import AirFresh
from miio.airfresh_t2017 import AirFreshA1, AirFreshT2017
from miio.airhumidifier import AirHumidifier
from miio.airhumidifier_jsq import AirHumidifierJsq
from miio.airhumidifier_miot import AirHumidifierMiot
from miio.airhumidifier_mjjsq import AirHumidifierMjjsq
from miio.airpurifier import AirPurifier
from miio.airpurifier_airdog import AirDogX3
from miio.airpurifier_miot import AirPurifierMiot
from miio.airqualitymonitor import AirQualityMonitor
from miio.airqualitymonitor_miot import AirQualityMonitorCGDN1
from miio.aqaracamera import AqaraCamera
from miio.chuangmi_camera import ChuangmiCamera
from miio.chuangmi_ir import ChuangmiIr
from miio.chuangmi_plug import ChuangmiPlug
from miio.cooker import Cooker
from miio.curtain_youpin import CurtainMiot
from miio.gateway import Gateway
from miio.heater import Heater
from miio.heater_miot import HeaterMiot
from miio.huizuo import Huizuo, HuizuoLampFan, HuizuoLampHeater, HuizuoLampScene
from miio.integrations.fan.dmaker import Fan1C, FanMiot, FanP5
from miio.integrations.fan.leshow import FanLeshow
from miio.integrations.fan.zhimi import Fan, FanZA5
from miio.integrations.humidifier.deerma import AirHumidifierJsqs
from miio.integrations.light.philips import (
    Ceil,
    PhilipsBulb,
    PhilipsEyecare,
    PhilipsMoonlight,
    PhilipsRwread,
    PhilipsWhiteBulb,
)
from miio.integrations.petwaterdispenser import PetWaterDispenser
from miio.integrations.vacuum.dreame.dreamevacuum_miot import DreameVacuum
from miio.integrations.vacuum.mijia import G1Vacuum
from miio.integrations.vacuum.roborock import RoborockVacuum, VacuumException
from miio.integrations.vacuum.roborock.vacuumcontainers import (
    CleaningDetails,
    CleaningSummary,
    ConsumableStatus,
    DNDStatus,
    Timer,
    VacuumStatus,
)
from miio.integrations.vacuum.roidmi.roidmivacuum_miot import RoidmiVacuumMiot
from miio.integrations.vacuum.viomi.viomivacuum import ViomiVacuum
from miio.integrations.yeelight import Yeelight
from miio.powerstrip import PowerStrip
from miio.protocol import Message, Utils
from miio.pwzn_relay import PwznRelay
from miio.scishare_coffeemaker import ScishareCoffee
from miio.toiletlid import Toiletlid
from miio.walkingpad import Walkingpad
from miio.waterpurifier import WaterPurifier
from miio.waterpurifier_yunmi import WaterPurifierYunmi
from miio.wifirepeater import WifiRepeater
from miio.wifispeaker import WifiSpeaker
from miio.yeelight_dual_switch import YeelightDualControlModule

from miio.discovery import Discovery

__version__ = version("python-miio")
