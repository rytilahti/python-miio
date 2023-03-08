# flake8: noqa
from importlib.metadata import version  # type: ignore

# Library imports need to be on top to avoid problems with
# circular dependencies. As these do not change that often
# they can be marked to be skipped for isort runs.

# isort: off

from miio.device import Device
from miio.devicestatus import DeviceStatus
from miio.exceptions import DeviceError, DeviceException, UnsupportedFeatureException
from miio.miot_device import MiotDevice
from miio.deviceinfo import DeviceInfo

# isort: on

from miio.cloud import CloudDeviceInfo, CloudException, CloudInterface
from miio.devicefactory import DeviceFactory
from miio.integrations.airdog.airpurifier import AirDogX3
from miio.integrations.cgllc.airmonitor import AirQualityMonitor, AirQualityMonitorCGDN1
from miio.integrations.chuangmi.camera import ChuangmiCamera
from miio.integrations.chuangmi.plug import ChuangmiPlug
from miio.integrations.chuangmi.remote import ChuangmiIr
from miio.integrations.chunmi.cooker import Cooker
from miio.integrations.deerma.humidifier import AirHumidifierJsqs, AirHumidifierMjjsq
from miio.integrations.dmaker.airfresh import AirFreshA1, AirFreshT2017
from miio.integrations.dmaker.fan import Fan1C, FanMiot, FanP5
from miio.integrations.dreame.vacuum import DreameVacuum
from miio.integrations.genericmiot.genericmiot import GenericMiot
from miio.integrations.huayi.light import (
    Huizuo,
    HuizuoLampFan,
    HuizuoLampHeater,
    HuizuoLampScene,
)
from miio.integrations.ijai.vacuum import Pro2Vacuum
from miio.integrations.ksmb.walkingpad import Walkingpad
from miio.integrations.leshow.fan import FanLeshow
from miio.integrations.lumi.acpartner import (
    AirConditioningCompanion,
    AirConditioningCompanionMcn02,
    AirConditioningCompanionV3,
)
from miio.integrations.lumi.camera.aqaracamera import AqaraCamera
from miio.integrations.lumi.curtain import CurtainMiot
from miio.integrations.lumi.gateway import Gateway
from miio.integrations.mijia.vacuum import G1Vacuum
from miio.integrations.mmgg.petwaterdispenser import PetWaterDispenser
from miio.integrations.nwt.dehumidifier import AirDehumidifier
from miio.integrations.philips.light import (
    Ceil,
    PhilipsBulb,
    PhilipsEyecare,
    PhilipsMoonlight,
    PhilipsRwread,
    PhilipsWhiteBulb,
)
from miio.integrations.pwzn.relay import PwznRelay
from miio.integrations.roborock.vacuum import RoborockVacuum
from miio.integrations.roidmi.vacuum import RoidmiVacuumMiot
from miio.integrations.scishare.coffee import ScishareCoffee
from miio.integrations.shuii.humidifier import AirHumidifierJsq
from miio.integrations.tinymu.toiletlid import Toiletlid
from miio.integrations.viomi.vacuum import ViomiVacuum
from miio.integrations.viomi.viomidishwasher import ViomiDishwasher
from miio.integrations.xiaomi.aircondition.airconditioner_miot import AirConditionerMiot
from miio.integrations.xiaomi.repeater.wifirepeater import WifiRepeater
from miio.integrations.xiaomi.wifispeaker.wifispeaker import WifiSpeaker
from miio.integrations.yeelight.dual_switch import YeelightDualControlModule
from miio.integrations.yeelight.light import Yeelight
from miio.integrations.yunmi.waterpurifier import WaterPurifier, WaterPurifierYunmi
from miio.integrations.zhimi.airpurifier import AirFresh, AirPurifier, AirPurifierMiot
from miio.integrations.zhimi.fan import Fan, FanZA5
from miio.integrations.zhimi.heater import Heater, HeaterMiot
from miio.integrations.zhimi.humidifier import AirHumidifier, AirHumidifierMiot
from miio.integrations.zimi.powerstrip import PowerStrip
from miio.protocol import Message, Utils
from miio.push_server import EventInfo, PushServer

from miio.discovery import Discovery

__version__ = version("python-miio")
