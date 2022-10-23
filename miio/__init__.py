# flake8: noqa
from importlib.metadata import version  # type: ignore

# Library imports need to be on top to avoid problems with
# circular dependencies. As these do not change that often
# they can be marked to be skipped for isort runs.

# isort: off

from miio.device import Device
from miio.devicestatus import DeviceStatus
from miio.exceptions import DeviceError, DeviceException
from miio.miot_device import MiotDevice
from miio.deviceinfo import DeviceInfo

# isort: on

# Integration imports
from miio.airconditioner_miot import AirConditionerMiot
from miio.airconditioningcompanion import (
    AirConditioningCompanion,
    AirConditioningCompanionV3,
)
from miio.airconditioningcompanionMCN import AirConditioningCompanionMcn02
from miio.airdehumidifier import AirDehumidifier
from miio.airqualitymonitor import AirQualityMonitor
from miio.airqualitymonitor_miot import AirQualityMonitorCGDN1
from miio.aqaracamera import AqaraCamera
from miio.chuangmi_camera import ChuangmiCamera
from miio.chuangmi_ir import ChuangmiIr
from miio.chuangmi_plug import ChuangmiPlug
from miio.cloud import CloudInterface
from miio.cooker import Cooker
from miio.curtain_youpin import CurtainMiot
from miio.devicefactory import DeviceFactory
from miio.gateway import Gateway
from miio.heater import Heater
from miio.heater_miot import HeaterMiot
from miio.huizuo import Huizuo, HuizuoLampFan, HuizuoLampHeater, HuizuoLampScene
from miio.integrations.airpurifier import (
    AirDogX3,
    AirFresh,
    AirFreshA1,
    AirFreshT2017,
    AirPurifier,
    AirPurifierMiot,
)
from miio.integrations.fan import Fan, Fan1C, FanLeshow, FanMiot, FanP5, FanZA5
from miio.integrations.humidifier import (
    AirHumidifier,
    AirHumidifierJsq,
    AirHumidifierJsqs,
    AirHumidifierMiot,
    AirHumidifierMjjsq,
)
from miio.integrations.light import (
    Ceil,
    PhilipsBulb,
    PhilipsEyecare,
    PhilipsMoonlight,
    PhilipsRwread,
    PhilipsWhiteBulb,
    Yeelight,
)
from miio.integrations.petwaterdispenser import PetWaterDispenser
from miio.integrations.vacuum import (
    DreameVacuum,
    G1Vacuum,
    Pro2Vacuum,
    RoborockVacuum,
    RoidmiVacuumMiot,
    VacuumException,
    ViomiVacuum,
)
from miio.integrations.vacuum.roborock.vacuumcontainers import (
    CleaningDetails,
    CleaningSummary,
    ConsumableStatus,
    DNDStatus,
    Timer,
    VacuumStatus,
)
from miio.integrations.viomidishwasher import ViomiDishwasher
from miio.powerstrip import PowerStrip
from miio.protocol import Message, Utils
from miio.push_server import EventInfo, PushServer
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
