# flake8: noqa
try:
    # python 3.7 and earlier
    from importlib_metadata import version  # type: ignore
except ImportError:
    # python 3.8 and later
    from importlib.metadata import version  # type: ignore

from miio.airconditioningcompanion import (
    AirConditioningCompanion,
    AirConditioningCompanionV3,
)
from miio.airconditioningcompanionMCN import AirConditioningCompanionMcn02
from miio.airdehumidifier import AirDehumidifier
from miio.airfresh import AirFresh, AirFreshVA4
from miio.airfresh_t2017 import AirFreshT2017
from miio.airhumidifier import AirHumidifier, AirHumidifierCA1, AirHumidifierCB1
from miio.airhumidifier_jsq import AirHumidifierJsq
from miio.airhumidifier_miot import AirHumidifierMiot
from miio.airhumidifier_mjjsq import AirHumidifierMjjsq
from miio.airpurifier import AirPurifier
from miio.airpurifier_miot import AirPurifierMiot
from miio.airqualitymonitor import AirQualityMonitor
from miio.aqaracamera import AqaraCamera
from miio.ceil import Ceil
from miio.chuangmi_camera import ChuangmiCamera
from miio.chuangmi_ir import ChuangmiIr
from miio.chuangmi_plug import ChuangmiPlug, Plug, PlugV1, PlugV3
from miio.cooker import Cooker
from miio.device import Device
from miio.exceptions import DeviceError, DeviceException
from miio.fan import Fan, FanP5, FanSA1, FanV2, FanZA1, FanZA4
from miio.gateway import Gateway
from miio.heater import Heater
from miio.philips_bulb import PhilipsBulb, PhilipsWhiteBulb
from miio.philips_eyecare import PhilipsEyecare
from miio.philips_moonlight import PhilipsMoonlight
from miio.philips_rwread import PhilipsRwread
from miio.powerstrip import PowerStrip
from miio.protocol import Message, Utils
from miio.pwzn_relay import PwznRelay
from miio.toiletlid import Toiletlid
from miio.vacuum import Vacuum, VacuumException
from miio.vacuumcontainers import (
    CleaningDetails,
    CleaningSummary,
    ConsumableStatus,
    DNDStatus,
    Timer,
    VacuumStatus,
)
from miio.viomivacuum import ViomiVacuum
from miio.waterpurifier import WaterPurifier
from miio.wifirepeater import WifiRepeater
from miio.wifispeaker import WifiSpeaker
from miio.yeelight import Yeelight

from miio.discovery import Discovery

__version__ = version("python-miio")
