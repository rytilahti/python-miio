import enum
import miio.vaxuum.base as basevacuum


class CustomEnum(enum.Enum):
    def as_base(self):
        for custom, base in self._basemap:
            if self == custom:
                return base
        return self._base_default

    @classmethod
    def from_base(cls, val):
        for custom, base in cls._basemap:
            if val == base:
                return custom
        return cls._default


class FanSpeed(CustomEnum):
    SILENT = 1
    STANDARD = 2
    STRONG = 3
    TURBO = 4


FanSpeed._base_default = basevacuum.FanSpeed.STANDARD
FanSpeed._default = FanSpeed.STANDARD
FanSpeed._basemap = [
    (FanSpeed.SILENT, basevacuum.FanSpeed.SILENT),
    (FanSpeed.STANDARD, basevacuum.FanSpeed.STANDARD),
    (FanSpeed.STRONG, basevacuum.FanSpeed.MEDIUM),
    (FanSpeed.TURBO, basevacuum.FanSpeed.TURBO),
    (FanSpeed.SILENT, basevacuum.FanSpeed.GENTLE),
]


class VacuumState(CustomEnum):
    UNKNOWN = 0

    CLEANING = 1
    IDLE = 2
    PAUSED = 3
    ERROR = 4
    GO_CHARGING = 5
    DOCKED = 6


VacuumState._base_default = basevacuum.VacuumState.UNKNOWN
VacuumState._default = VacuumState.UNKNOWN
VacuumState._basemap = [
    (VacuumState.CLEANING, basevacuum.VacuumState.CLEANING),
    (VacuumState.IDLE, basevacuum.VacuumState.IDLE),
    (VacuumState.PAUSED, basevacuum.VacuumState.PAUSED),
    (VacuumState.ERROR, basevacuum.VacuumState.ERROR),
    (VacuumState.GO_CHARGING, basevacuum.VacuumState.RETURNING_TO_DOCK),
    (VacuumState.DOCKED, basevacuum.VacuumState.DOCKED),
]

class ChargeStatus(CustomEnum):
    UNKNOWN = 0

    # is currently charging
    CHARGING = 1
    # is currently discharging
    DISCHARGING = 2
    # battery is full
    FULL = 3
    # on the way to dock to charge
    GO_CHARGING = 4

ChargeStatus._base_default = basevacuum.ChargeStatus.UNKNOWN
ChargeStatus._default = ChargeStatus.UNKNOWN
ChargeStatus._basemap = [
    (ChargeStatus.CHARGING, basevacuum.ChargeStatus.CHARGING),
    (ChargeStatus.DISCHARGING, basevacuum.ChargeStatus.DISCHARGING),
    (ChargeStatus.FULL, basevacuum.ChargeStatus.FULL),
    (ChargeStatus.GO_CHARGING, basevacuum.ChargeStatus.GO_CHARGING),
]
