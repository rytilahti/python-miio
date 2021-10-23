import enum
import logging

from miio.exceptions import DeviceException

_LOGGER = logging.getLogger(__name__)

MODEL_EG1 = "chunmi.ihcooker.eg1"
MODEL_EXP1 = "chunmi.ihcooker.exp1"
MODEL_FW = "chunmi.ihcooker.chefnic"
MODEL_HK1 = "chunmi.ihcooker.hk1"
MODEL_KOREA1 = "chunmi.ihcooker.korea1"
MODEL_TW1 = "chunmi.ihcooker.tw1"
MODEL_V1 = "chunmi.ihcooker.v1"

MODEL_VERSION1 = [MODEL_V1, MODEL_FW, MODEL_HK1, MODEL_TW1]
MODEL_VERSION2 = [MODEL_EG1, MODEL_EXP1, MODEL_KOREA1]
SUPPORTED_MODELS = MODEL_VERSION1 + MODEL_VERSION2

DEVICE_ID = {
    MODEL_EG1: 4,
    MODEL_EXP1: 4,
    MODEL_FW: 7,
    MODEL_HK1: 2,
    MODEL_KOREA1: 5,
    MODEL_TW1: 3,
    MODEL_V1: 1,
}


class IHCookerException(DeviceException):
    pass


class OperationMode(enum.Enum):
    """Global mode the induction cooker is currently in."""

    Error = "error"
    Finish = "finish"
    Offline = "offline"
    Pause = "pause"
    TimerPaused = "pause_time"
    Precook = "precook"
    Running = "running"
    SetClock = "set01"
    SetStartTime = "set02"
    SetCookingTime = "set03"
    Shutdown = "shutdown"
    Timing = "timing"
    Waiting = "waiting"


class StageMode(enum.IntEnum):
    """Mode for current stage of recipe."""

    FireMode = 0
    TemperatureMode = 2
    Unknown4 = 4
    TempAutoSmallPot = 8  # TODO: verify this is the right behaviour.
    Unknown10 = 10
    TempAutoBigPot = 24  # TODO: verify this is the right behaviour.
    Unknown16 = 16
