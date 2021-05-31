import enum

from miio.device import DeviceStatus
from typing import Optional


class VacuumState(enum.Enum):
    UNKNOWN = 0
    # Cleaning in progress
    CLEANING = 1
    # Doing nothing
    IDLE = 2
    # Cleaning is paused
    PAUSED = 3
    ERROR = 4
    RETURNING_TO_DOCK = 5
    DOCKED = 6
    # MANUAL = 7


class CleaningType(enum.Enum):
    UNKNOWN = 0
    NORMAL = 1
    ZONE = 2
    SEGMENT = 3


class ChargeStatus(enum.Enum):
    UNKNOWN = 0

    # is currently charging
    CHARGING = 1
    # is currently discharging
    DISCHARGING = 2
    # battery is full
    FULL = 3
    # on the way to dock to charge
    GO_CHARGING = 4


class FanSpeed(enum.Enum):
    """Human readable vacuum fan speed presets

    If mode is not supported on current model, closest should be used
      (for example, SILENT instead of GENTLE)
    If mode is unknown, set to STANDARD
    """
    SILENT = 1
    STANDARD = 2
    MEDIUM = 3  # called strong for some models
    TURBO = 4
    GENTLE = 5  # exclusive mopping

class VacuumStatus(DeviceStatus):
    @property
    def state(self) -> VacuumState:
        """Get current state """
        raise NotImplementedError

    @property
    def charge_status(self) -> ChargeStatus:
        """Get battery status """
        raise NotImplementedError

    @property
    def battery_level(self) -> int:
        """Get battery percentage """
        raise NotImplementedError

    @property
    def fan_speed(self) -> FanSpeed:
        """ get current fan speed """
        raise NotImplementedError

    @property
    def cleaning_type(self) -> CleaningType:
        """ get current cleaning type """
        raise NotImplementedError

    # todo: VacuumError type
    @property
    def error(self) -> Optional[str]:
        """ get current error, if any """
        raise NotImplementedError

class ConsumableStatus(DeviceStatus):
    pass
