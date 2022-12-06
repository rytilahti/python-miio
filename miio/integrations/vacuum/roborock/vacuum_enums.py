import enum


class TimerState(enum.Enum):
    On = "on"
    Off = "off"


class Consumable(enum.Enum):
    MainBrush = "main_brush_work_time"
    SideBrush = "side_brush_work_time"
    Filter = "filter_work_time"
    SensorDirty = "sensor_dirty_time"
    CleaningBrush = "cleaning_brush_work_times"
    Strainer = "strainer_work_times"


class FanspeedEnum(enum.Enum):
    pass


class FanspeedV1(FanspeedEnum):
    Silent = 38
    Standard = 60
    Medium = 77
    Turbo = 90


class FanspeedV2(FanspeedEnum):
    Silent = 101
    Standard = 102
    Medium = 103
    Turbo = 104
    Gentle = 105
    Auto = 106


class FanspeedV3(FanspeedEnum):
    Silent = 38
    Standard = 60
    Medium = 75
    Turbo = 100


class FanspeedE2(FanspeedEnum):
    # Original names from the app: Gentle, Silent, Standard, Strong, Max
    Gentle = 41
    Silent = 50
    Standard = 68
    Medium = 79
    Turbo = 100


class FanspeedS7(FanspeedEnum):
    Off = 105
    Silent = 101
    Standard = 102
    Medium = 103
    Turbo = 104


class FanspeedS7_Maxv(FanspeedEnum):
    # Original names from the app: Quiet, Balanced, Turbo, Max, Max+
    Off = 105
    Silent = 101
    Standard = 102
    Medium = 103
    Turbo = 104
    Max = 108


class WaterFlow(enum.Enum):
    """Water flow strength on s5 max."""

    Minimum = 200
    Low = 201
    High = 202
    Maximum = 203


class MopMode(enum.Enum):
    """Mop routing on S7 + S7MAXV."""

    Standard = 300
    Deep = 301
    DeepPlus = 303


class MopIntensity(enum.Enum):
    """Mop scrub intensity on S7 + S7MAXV."""

    Off = 200
    Mild = 201
    Moderate = 202
    Intense = 203


class CarpetCleaningMode(enum.Enum):
    """Type of carpet cleaning/avoidance."""

    Avoid = 0
    Rise = 1
    Ignore = 2


class DustCollectionMode(enum.Enum):
    """Auto emptying mode (S7 + S7MAXV only)"""

    Smart = 0
    Quick = 1
    Daily = 2
    Strong = 3
    Max = 4
