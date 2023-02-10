from enum import Enum


class VacuumId(Enum):
    """Vacuum-specific standardized descriptor identifiers.

    TODO: this is a temporary solution, and might be named to 'Vacuum' later on.
    """

    # Actions
    Start = "vacuum:start-sweep"
    Stop = "vacuum:stop-sweeping"
    Pause = "vacuum:pause-sweeping"
    ReturnHome = "battery:start-charge"
    Locate = "identify:identify"

    # Settings
    FanSpeed = "vacuum:fan-speed"  # TODO: invented name
    FanSpeedPreset = "vacuum:mode"

    # Sensors
    State = "vacuum:status"
    ErrorMessage = "vacuum:fault"
    Battery = "battery:level"
