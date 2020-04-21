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


class FaultStatus(Enum):
    No_faults = 0


class VacuumStatus(Enum):
    Sweeping = 1
    Idle = 2
    Paused = 3
    Error = 4
    Go_charging = 5
    Charging = 6


@dataclass
class DreameStatus:
    _max_properties = 9  # TODO: amount unknown, 9 should still work tho
    # siid 2: (Battery): 2 props, 1 actions
    # piid: 1 (Battery Level): (uint8, unit: percentage) (acc: ['read', 'notify'], value-list: [], value-range: [0, 100, 1])
    battery_level: int = field(
        metadata={"siid": 2, "piid": 1, "access": ["read", "notify"]}
    )
    # piid: 2 (Charging State): (uint8, unit: None) (acc: ['read', 'notify'], value-list: [{'value': 1, 'description': 'Charging'}, {'value': 2, 'description': 'Not Charging'}, {'value': 4, 'description': 'Charging'}, {'value': 5, 'description': 'Go Charging'}], value-range: None)
    charging_state: int = field(
        metadata={"siid": 2, "piid": 2, "access": ["read", "notify"]}
    )
    # siid 1: (Device Information): 4 props, 0 actions
    # piid: 4 (Current Firmware Version): (string, unit: None) (acc: ['read'], value-list: [], value-range: None)
    current_firmware_version: str = field(
        metadata={"siid": 1, "piid": 4, "access": ["read"]}
    )
    # piid: 1 (Device Manufacturer): (string, unit: None) (acc: ['read'], value-list: [], value-range: None)
    device_manufacturer: str = field(
        metadata={"siid": 1, "piid": 1, "access": ["read"]}
    )
    # piid: 2 (Device Model): (string, unit: None) (acc: ['read'], value-list: [], value-range: None)
    device_model: str = field(metadata={"siid": 1, "piid": 2, "access": ["read"]})
    # piid: 3 (Device Serial Number): (string, unit: None) (acc: ['read'], value-list: [], value-range: None)
    device_serial_number: str = field(
        metadata={"siid": 1, "piid": 3, "access": ["read"]}
    )
    # siid 3: (Robot Cleaner): 2 props, 2 actions
    # piid: 1 (Device Fault): (uint8, unit: None) (acc: ['read', 'notify'], value-list: [{'value': 0, 'description': 'No faults'}], value-range: None)
    device_fault: int = field(
        metadata={"siid": 3, "piid": 1, "access": ["read", "notify"]}
    )
    # piid: 2 (Status): (int8, unit: None) (acc: ['read', 'notify'], value-list: [{'value': 1, 'description': 'Sweeping'}, {'value': 2, 'description': 'Idle'}, {'value': 3, 'description': 'Paused'}, {'value': 4, 'description': 'Error'}, {'value': 5, 'description': 'Go Charging'}, {'value': 6, 'description': 'Charging'}], value-range: None)
    status: int = field(metadata={"siid": 3, "piid": 2, "access": ["read", "notify"]})
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
    # 工作模式: int = field(metadata={'siid': 18, 'piid': 1, 'access': ['read', 'notify']})
    # piid: 4 (area): (string, unit: None) (acc: ['read', 'write'], value-list: [], value-range: None)
    area: str = field(metadata={"siid": 18, "piid": 4, "access": ["read", "write"]})
    # piid: 5 (timer): (string, unit: None) (acc: ['read', 'write'], value-list: [], value-range: None)
    timer: str = field(metadata={"siid": 18, "piid": 5, "access": ["read", "write"]})
    # piid: 6 (清扫模式): (int32, unit: none) (acc: ['read', 'write', 'notify'], value-list: [{'value': 0, 'description': '安静'}, {'value': 1, 'description': '标准'}, {'value': 2, 'description': '中档'}, {'value': 3, 'description': '强力'}], value-range: None)
    # 清扫模式: int = field(metadata={'siid': 18, 'piid': 6, 'access': ['read', 'write', 'notify']})
    # piid: 8 (delete-timer): (int32, unit: None) (acc: ['write'], value-list: [], value-range: [0, 100, 1])
    # delete_timer: int = field(metadata={"siid": 18, "piid": 8, "access": ["write"]})
    # piid: 13 (): (uint32, unit: minutes) (acc: ['read', 'notify'], value-list: [], value-range: [0, 4294967295, 1])
    #: int = field(metadata={'siid': 18, 'piid': 13, 'access': ['read', 'notify']})
    # piid: 14 (): (uint32, unit: None) (acc: ['read', 'notify'], value-list: [], value-range: [0, 4294967295, 1])
    #: int = field(metadata={'siid': 18, 'piid': 14, 'access': ['read', 'notify']})
    # piid: 15 (): (uint32, unit: None) (acc: ['read', 'notify'], value-list: [], value-range: [0, 4294967295, 1])
    #: int = field(metadata={'siid': 18, 'piid': 15, 'access': ['read', 'notify']})
    # piid: 16 (): (uint32, unit: None) (acc: ['read', 'notify'], value-list: [], value-range: [0, 4294967295, 1])
    #: int = field(metadata={'siid': 18, 'piid': 16, 'access': ['read', 'notify']})
    # piid: 17 (): (uint16, unit: None) (acc: ['read', 'notify'], value-list: [], value-range: [0, 100, 1])
    #: int = field(metadata={'siid': 18, 'piid': 17, 'access': ['read', 'notify']})
    # piid: 18 (): (uint8, unit: None) (acc: ['read', 'notify'], value-list: [{'value': 0, 'description': ''}, {'value': 1, 'description': ''}], value-range: None)
    #: int = field(metadata={'siid': 18, 'piid': 18, 'access': ['read', 'notify']})
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
    enable: bool = field(metadata={"siid": 20, "piid": 1, "access": ["read", "write"]})
    # piid: 2 (start-time): (string, unit: None) (acc: ['read', 'write'], value-list: [], value-range: None)
    start_time: str = field(
        metadata={"siid": 20, "piid": 2, "access": ["read", "write"]}
    )
    # piid: 3 (stop-time): (string, unit: None) (acc: ['read', 'write'], value-list: [], value-range: None)
    stop_time: str = field(
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
    volume: int = field(
        metadata={"siid": 24, "piid": 1, "access": ["read", "write", "notify"]}
    )
    # piid: 3 (语音包ID): (string, unit: none) (acc: ['read', 'write'], value-list: [], value-range: None)
    # 语音包id: str = field(metadata={'siid': 24, 'piid': 3, 'access': ['read', 'write']})
    # siid 25: (): 1 props, 0 actions
    # piid: 1 (): (string, unit: None) (acc: ['read', 'notify'], value-list: [], value-range: None)
    # : str = field(metadata={'siid': 25, 'piid': 1, 'access': ['read', 'notify']})


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
    def start_charge(self) -> None:
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
    def identify(self) -> None:
        """aiid 1 Identify: in: [] -> out: []"""
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
    def 开始清扫(self) -> None:
        """aiid 1 开始清扫: in: [] -> out: []"""
        return self.call_action(18, 1)

    # aiid 2 stop-clean: in: [] -> out: []
    @command()
    def stop_clean(self) -> None:
        """aiid 2 stop-clean: in: [] -> out: []"""
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
    def map_req(self, _) -> None:
        """aiid 1 map-req: in: [2] -> out: []"""
        return self.call_action(23, 1)

    # siid 24: (audio): 2 props, 3 actions
    # aiid 1 : in: [] -> out: []
    @command()
    def UNKNOWN(self) -> None:
        """aiid 1 : in: [] -> out: []"""
        return self.call_action(24, 1)

    # aiid 2 : in: [] -> out: []
    @command()
    def UNKNOWN2(self) -> None:
        """aiid 2 : in: [] -> out: []"""
        return self.call_action(24, 2)

    # aiid 3 : in: [] -> out: []
    @command()
    def UNKNOWN3(self) -> None:
        """aiid 3 : in: [] -> out: []"""
        return self.call_action(24, 3)
