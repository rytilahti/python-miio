import logging
from dataclasses import dataclass, field
from enum import Enum

from .click_common import command
from .miot_device import MiotDevice

_LOGGER = logging.getLogger(__name__)


class ChargeStatus(Enum):
    Charging = 1
    Not_charging = 2
    Charging2 = 4
    Go_charging = 5


class Error(Enum):
    NoError = 0
    Drop = 1
    Cliff = 2
    Bumper = 3
    Gesture = 4
    Bumper_repeat = 5
    Drop_repeat = 6
    Optical_flow = 7
    No_box = 8
    No_tankbox = 9
    Waterbox_empty = 10
    Box_full = 11
    Brush = 12
    Side_brush = 13
    Fan = 14
    Left_wheel_motor = 15
    Right_wheel_motor = 16
    Turn_suffocate = 17
    Forward_suffocate = 18
    Charger_get = 19
    Battery_low = 20
    Charge_fault = 21
    Battery_percentage = 22
    Heart = 23
    Camera_occlusion = 24
    Camera_fault = 25
    Event_battery = 26
    Forward_looking = 27
    Gyroscope = 28


class VacuumStatus(Enum):
    Sweeping = 1
    Idle = 2
    Paused = 3
    Error = 4
    Go_charging = 5
    Charging = 6


class VacuumSpeed(Enum):
    """Fan speeds, same as for ViomiVacuum."""

    Silent = 0
    Standard = 1
    Medium = 2
    Turbo = 3


@dataclass
class DreameStatus:
    _max_properties = 14
    # siid 2: (Battery): 2 props, 1 actions
    # piid: 1 (Battery Level): (uint8, unit: percentage) (acc: ['read', 'notify'], value-list: [], value-range: [0, 100, 1])
    battery: int = field(metadata={"siid": 2, "piid": 1, "access": ["read", "notify"]})
    # piid: 2 (Charging State): (uint8, unit: None) (acc: ['read', 'notify'], value-list: [{'value': 1, 'description': 'Charging'}, {'value': 2, 'description': 'Not Charging'}, {'value': 4, 'description': 'Charging'}, {'value': 5, 'description': 'Go Charging'}], value-range: None)
    state: int = field(
        metadata={
            "siid": 2,
            "piid": 2,
            "access": ["read", "notify"],
            "enum": ChargeStatus,
        }
    )
    # siid 3: (Robot Cleaner): 2 props, 2 actions
    # piid: 1 (Device Fault): (uint8, unit: None) (acc: ['read', 'notify'], value-list: [{'value': 0, 'description': 'No faults'}], value-range: None)
    error: int = field(
        metadata={"siid": 3, "piid": 1, "access": ["read", "notify"], "enum": Error}
    )
    # piid: 2 (Status): (int8, unit: None) (acc: ['read', 'notify'], value-list: [{'value': 1, 'description': 'Sweeping'}, {'value': 2, 'description': 'Idle'}, {'value': 3, 'description': 'Paused'}, {'value': 4, 'description': 'Error'}, {'value': 5, 'description': 'Go Charging'}, {'value': 6, 'description': 'Charging'}], value-range: None)
    status: int = field(
        metadata={
            "siid": 3,
            "piid": 2,
            "access": ["read", "notify"],
            "enum": VacuumStatus,
        }
    )
    # siid 17: (Identify): 0 props, 1 actions
    # siid 26: (Main Cleaning Brush): 2 props, 1 actions
    # piid: 1 (Brush Left Time): (uint16, unit: hour) (acc: ['read', 'notify'], value-list: [], value-range: [0, 300, 1])
    brush_left_time: int = field(
        metadata={"siid": 26, "piid": 1, "access": ["read", "notify"]}
    )
    # piid: 2 (Brush Life Level): (uint8, unit: percentage) (acc: ['read', 'notify'], value-list: [], value-range: [0, 100, 1])
    brush_life_level: int = field(
        metadata={"siid": 26, "piid": 2, "access": ["read", "notify"]}
    )
    # siid 27: (Filter): 2 props, 1 actions
    # piid: 1 (Filter Life Level): (uint8, unit: percentage) (acc: ['read', 'notify'], value-list: [], value-range: [0, 100, 1])
    filter_life_level: int = field(
        metadata={"siid": 27, "piid": 1, "access": ["read", "notify"]}
    )
    # piid: 2 (Filter Left Time): (uint16, unit: hour) (acc: ['read', 'notify'], value-list: [], value-range: [0, 300, 1])
    filter_left_time: int = field(
        metadata={"siid": 27, "piid": 2, "access": ["read", "notify"]}
    )
    # siid 28: (Side Cleaning Brush): 2 props, 1 actions
    # piid: 1 (Brush Left Time): (uint16, unit: hour) (acc: ['read', 'notify'], value-list: [], value-range: [0, 300, 1])
    brush_left_time2: int = field(
        metadata={"siid": 28, "piid": 1, "access": ["read", "notify"]}
    )
    # piid: 2 (Brush Life Level): (uint8, unit: percentage) (acc: ['read', 'notify'], value-list: [], value-range: [0, 100, 1])
    brush_life_level2: int = field(
        metadata={"siid": 28, "piid": 2, "access": ["read", "notify"]}
    )
    # siid 18: (clean): 16 props, 2 actions
    # piid: 1 (工作模式): (int32, unit: none) (acc: ['read', 'notify'], value-list: [], value-range: [0, 17, 1])
    operating_mode: int = field(
        metadata={"siid": 18, "piid": 1, "access": ["read", "notify"]}
    )
    # piid: 4 (area): (string, unit: None) (acc: ['read', 'write'], value-list: [], value-range: None)
    area: str = field(metadata={"siid": 18, "piid": 4, "access": ["read", "write"]})
    # piid: 5 (timer): (string, unit: None) (acc: ['read', 'write'], value-list: [], value-range: None)
    timer: str = field(metadata={"siid": 18, "piid": 5, "access": ["read", "write"]})
    # piid: 6 (清扫模式): (int32, unit: none) (acc: ['read', 'write', 'notify'], value-list: [{'value': 0, 'description': '安静'}, {'value': 1, 'description': '标准'}, {'value': 2, 'description': '中档'}, {'value': 3, 'description': '强力'}], value-range: None)
    fan_speed: int = field(
        metadata={
            "siid": 18,
            "piid": 6,
            "access": ["read", "write", "notify"],
            "enum": VacuumSpeed,
        }
    )
    # piid: 8 (delete-timer): (int32, unit: None) (acc: ['write'], value-list: [], value-range: [0, 100, 1])
    # delete_timer: int = field(metadata={"siid": 18, "piid": 8, "access": ["write"]})
    # piid: 13 (): (uint32, unit: minutes) (acc: ['read', 'notify'], value-list: [], value-range: [0, 4294967295, 1])
    last_clean: int = field(
        metadata={"siid": 18, "piid": 13, "access": ["read", "notify"]}
    )
    # piid: 14 (): (uint32, unit: None) (acc: ['read', 'notify'], value-list: [], value-range: [0, 4294967295, 1])
    total_clean_count: int = field(
        metadata={"siid": 18, "piid": 14, "access": ["read", "notify"]}
    )
    # piid: 15 (): (uint32, unit: None) (acc: ['read', 'notify'], value-list: [], value-range: [0, 4294967295, 1])
    total_area: int = field(
        metadata={"siid": 18, "piid": 15, "access": ["read", "notify"]}
    )
    # piid: 16 (): (uint32, unit: None) (acc: ['read', 'notify'], value-list: [], value-range: [0, 4294967295, 1])
    total_log_start: int = field(
        metadata={"siid": 18, "piid": 16, "access": ["read", "notify"]}
    )
    # piid: 17 (): (uint16, unit: None) (acc: ['read', 'notify'], value-list: [], value-range: [0, 100, 1])
    button_led: int = field(
        metadata={"siid": 18, "piid": 17, "access": ["read", "notify"]}
    )
    # piid: 18 (): (uint8, unit: None) (acc: ['read', 'notify'], value-list: [{'value': 0, 'description': ''}, {'value': 1, 'description': ''}], value-range: None)
    clean_success: int = field(
        metadata={"siid": 18, "piid": 18, "access": ["read", "notify"]}
    )
    # siid 19: (consumable): 3 props, 0 actions
    # piid: 1 (life-sieve): (string, unit: None) (acc: ['read', 'write'], value-list: [], value-range: None)
    life_sieve: str = field(
        metadata={"siid": 19, "piid": 1, "access": ["read", "write"]}
    )
    # piid: 2 (life-brush-side): (string, unit: None) (acc: ['read', 'write'], value-list: [], value-range: None)
    life_brush_side: str = field(
        metadata={"siid": 19, "piid": 2, "access": ["read", "write"]}
    )
    # piid: 3 (life-brush-main): (string, unit: None) (acc: ['read', 'write'], value-list: [], value-range: None)
    life_brush_main: str = field(
        metadata={"siid": 19, "piid": 3, "access": ["read", "write"]}
    )
    # siid 20: (annoy): 3 props, 0 actions
    # piid: 1 (enable): (bool, unit: None) (acc: ['read', 'write'], value-list: [], value-range: None)
    dnd_enabled: bool = field(
        metadata={"siid": 20, "piid": 1, "access": ["read", "write"]}
    )
    # piid: 2 (start-time): (string, unit: None) (acc: ['read', 'write'], value-list: [], value-range: None)
    dnd_start_time: str = field(
        metadata={"siid": 20, "piid": 2, "access": ["read", "write"]}
    )
    # piid: 3 (stop-time): (string, unit: None) (acc: ['read', 'write'], value-list: [], value-range: None)
    dnd_stop_time: str = field(
        metadata={"siid": 20, "piid": 3, "access": ["read", "write"]}
    )
    # siid 21: (remote): 2 props, 3 actions
    # piid: 1 (deg): (string, unit: None) (acc: ['write'], value-list: [], value-range: None)
    # deg: str = field(metadata={"siid": 21, "piid": 1, "access": ["write"]})
    # piid: 2 (speed): (string, unit: None) (acc: ['write'], value-list: [], value-range: None)
    # speed: str = field(metadata={"siid": 21, "piid": 2, "access": ["write"]})
    # siid 22: (warn): 1 props, 0 actions
    # siid 23: (map): 3 props, 1 actions
    # piid: 1 (map-view): (string, unit: None) (acc: ['read', 'notify'], value-list: [], value-range: None)
    map_view: str = field(
        metadata={"siid": 23, "piid": 1, "access": ["read", "notify"]}
    )
    # piid: 2 (frame-info): (string, unit: None) (acc: ['write'], value-list: [], value-range: None)
    # frame_info: str = field(metadata={"siid": 23, "piid": 2, "access": ["write"]})
    # siid 24: (audio): 2 props, 3 actions
    # piid: 1 (volume): (int32, unit: None) (acc: ['read', 'write', 'notify'], value-list: [], value-range: [0, 100, 1])
    audio_volume: int = field(
        metadata={"siid": 24, "piid": 1, "access": ["read", "write", "notify"]}
    )
    # piid: 3 (语音包ID): (string, unit: none) (acc: ['read', 'write'], value-list: [], value-range: None)
    audio_language: str = field(
        metadata={"siid": 24, "piid": 3, "access": ["read", "write"]}
    )
    # siid 25: (): 1 props, 0 actions
    # piid: 1 (): (string, unit: None) (acc: ['read', 'notify'], value-list: [], value-range: None)
    timezone: str = field(
        metadata={"siid": 25, "piid": 1, "access": ["read", "notify"]}
    )


class DreameVacuum(MiotDevice):
    """Support for dreame vacuum (1C STYTJ01ZHM, dreame.vacuum.mc1808)."""

    _MAPPING = DreameStatus

    @command()
    def status(self) -> DreameStatus:
        return self.get_properties_for_dataclass(DreameStatus)

    def call_action(self, siid, aiid, params=None):
        # {"did":"<mydeviceID>","siid":18,"aiid":1,"in":[{"piid":1,"value":2}]
        if params is None:
            params = []
        payload = {
            "did": f"call-{siid}-{aiid}",
            "siid": siid,
            "aiid": aiid,
            "in": params,
        }
        return self.send("action", payload)

    # siid 2: (Battery): 2 props, 1 actions
    # aiid 1 Start Charge: in: [] -> out: []
    @command()
    def return_home(self) -> None:
        """aiid 1 Start Charge: in: [] -> out: []"""
        return self.call_action(2, 1)

    # siid 3: (Robot Cleaner): 2 props, 2 actions
    # aiid 1 Start Sweep: in: [] -> out: []
    @command()
    def start_sweep(self) -> None:
        """aiid 1 Start Sweep: in: [] -> out: []"""
        return self.call_action(3, 1)

    # aiid 2 Stop Sweeping: in: [] -> out: []
    @command()
    def stop_sweeping(self) -> None:
        """aiid 2 Stop Sweeping: in: [] -> out: []"""
        return self.call_action(3, 2)

    # siid 17: (Identify): 0 props, 1 actions
    # aiid 1 Identify: in: [] -> out: []
    @command()
    def find(self) -> None:
        """Find the robot."""
        return self.call_action(17, 1)

    # siid 26: (Main Cleaning Brush): 2 props, 1 actions
    # aiid 1 Reset Brush Life: in: [] -> out: []
    @command()
    def reset_brush_life(self) -> None:
        """aiid 1 Reset Brush Life: in: [] -> out: []"""
        return self.call_action(26, 1)

    # siid 27: (Filter): 2 props, 1 actions
    # aiid 1 Reset Filter Life: in: [] -> out: []
    @command()
    def reset_filter_life(self) -> None:
        """aiid 1 Reset Filter Life: in: [] -> out: []"""
        return self.call_action(27, 1)

    # siid 28: (Side Cleaning Brush): 2 props, 1 actions
    # aiid 1 Reset Brush Life: in: [] -> out: []
    @command()
    def reset_brush_life2(self) -> None:
        """aiid 1 Reset Brush Life: in: [] -> out: []"""
        return self.call_action(28, 1)

    # siid 18: (clean): 16 props, 2 actions
    # aiid 1 开始清扫: in: [] -> out: []
    @command()
    def start(self) -> None:
        """Start cleaning."""
        # TODO: find out other values
        payload = [{"piid": 1, "value": 2}]
        return self.call_action(18, 1, payload)

    # aiid 2 stop-clean: in: [] -> out: []
    @command()
    def stop(self) -> None:
        """Stop cleaning."""
        return self.call_action(18, 2)

    # siid 21: (remote): 2 props, 3 actions
    # aiid 1 start-remote: in: [1, 2] -> out: []
    @command()
    def start_remote(self, _) -> None:
        """aiid 1 start-remote: in: [1, 2] -> out: []"""
        return self.call_action(21, 1)

    # aiid 2 stop-remote: in: [] -> out: []
    @command()
    def stop_remote(self) -> None:
        """aiid 2 stop-remote: in: [] -> out: []"""
        return self.call_action(21, 2)

    # aiid 3 exit-remote: in: [] -> out: []
    @command()
    def exit_remote(self) -> None:
        """aiid 3 exit-remote: in: [] -> out: []"""
        return self.call_action(21, 3)

    # siid 23: (map): 3 props, 1 actions
    # aiid 1 map-req: in: [2] -> out: []
    @command()
    def map_req(self) -> None:
        """aiid 1 map-req: in: [2] -> out: []"""
        return self.call_action(23, 1)

    # siid 24: (audio): 2 props, 3 actions
    # aiid 1 : in: [] -> out: []
    @command()
    def audio_position(self) -> None:
        """TODO"""
        return self.call_action(24, 1)

    # aiid 2 : in: [] -> out: []
    @command()
    def install_voice_pack(self) -> None:
        """Install given voice pack."""
        payload = [
            {"piid": 3, "value": "EN"},  # language code
            {"piid": 4, "value": "http://url"},
            {"piid": 5, "value": "md5sum for the pack"},
            {"piid": 6, "value": "size of the pack"},
        ]
        return self.call_action(24, 2, payload)

    # aiid 3 : in: [] -> out: []
    @command()
    def test_sound(self) -> None:
        """aiid 3 : in: [] -> out: []"""
        return self.call_action(24, 3)
