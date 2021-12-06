# flake8: noqa
try:
    # python 3.7 and earlier
    from importlib_metadata import version  # type: ignore
except ImportError:
    # python 3.8 and later
    from importlib.metadata import version  # type: ignore

from miio.airconditioner_miot import AirConditionerMiot
from miio.airconditioningcompanion import (
    AirConditioningCompanion,
    AirConditioningCompanionV3,
)
from miio.airconditioningcompanionMCN import AirConditioningCompanionMcn02
from miio.airdehumidifier import AirDehumidifier
from miio.airfresh import AirFresh, AirFreshVA4
from miio.airfresh_t2017 import AirFreshA1, AirFreshT2017
from miio.airhumidifier import AirHumidifier, AirHumidifierCA1, AirHumidifierCB1
from miio.airhumidifier_jsq import AirHumidifierJsq
from miio.airhumidifier_miot import AirHumidifierMiot
from miio.airhumidifier_mjjsq import AirHumidifierMjjsq
from miio.airpurifier import AirPurifier
from miio.airpurifier_airdog import AirDogX3, AirDogX5, AirDogX7SM
from miio.airpurifier_miot import AirPurifierMB4, AirPurifierMiot
from miio.airqualitymonitor import AirQualityMonitor
from miio.airqualitymonitor_miot import AirQualityMonitorCGDN1
from miio.aqaracamera import AqaraCamera
from miio.ceil import Ceil
from miio.chuangmi_camera import ChuangmiCamera
from miio.chuangmi_ir import ChuangmiIr
from miio.chuangmi_plug import ChuangmiPlug, Plug, PlugV1, PlugV3
from miio.cooker import Cooker
from miio.curtain_youpin import CurtainMiot
from miio.device import Device, DeviceStatus
from miio.exceptions import DeviceError, DeviceException
from miio.fan import Fan, FanP5, FanSA1, FanV2, FanZA1, FanZA4
from miio.fan_leshow import FanLeshow
from miio.fan_miot import Fan1C, FanMiot, FanP9, FanP10, FanP11, FanZA5
from miio.gateway import Gateway
from miio.heater import Heater
from miio.heater_miot import HeaterMiot
from miio.huizuo import Huizuo, HuizuoLampFan, HuizuoLampHeater, HuizuoLampScene
from miio.integrations.petwaterdispenser import PetWaterDispenser
from miio.integrations.petfooddispenser import PetFoodDispenser
from miio.integrations.vacuum.dreame.dreamevacuum_miot import DreameVacuumMiot
from miio.integrations.vacuum.mijia import G1Vacuum
from miio.integrations.vacuum.roborock import RoborockVacuum, Vacuum, VacuumException
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
from miio.miot_device import MiotDevice
from miio.philips_bulb import PhilipsBulb, PhilipsWhiteBulb
from miio.philips_eyecare import PhilipsEyecare
from miio.philips_moonlight import PhilipsMoonlight
from miio.philips_rwread import PhilipsRwread
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
