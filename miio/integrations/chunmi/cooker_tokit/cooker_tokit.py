import logging
import math
from collections import defaultdict
from datetime import datetime, time, timedelta
from typing import List, Optional

import click

from miio.click_common import command, format_output
from miio.device import Device, DeviceStatus

_LOGGER = logging.getLogger(__name__)

MODEL_TK4001 = "tokit.cooker.tk4001"
UNKNOWN = "UNKNOWN"

STATUS_MAPPING = {
    "1": "IDLE",
    "2": "RUNNING",
    "3": "KEEPWARM",
    "4": "RESERVATION",
    "8": "UNUSUAL",
    "13": "FINISH",
}

COOK_MODE_NAME_MAPPING = {
    "精煮饭": "00000001",
    "快煮饭": "00000002",
    "煮粥": "00000003",
    "保温": "00000004",
    "蒸煮": "00000005",
    "炖汤": "00000006",
    "蛋糕": "00000007",
    "酸奶": "00000008",
    "热饭": "00000011",
    "小米粥": "00000014",
    "八宝粥": "00000015",
    "煲仔饭": "00000016",
    "香甜煮": "00000017",
    "发芽饭": "00000080",
}

COOK_MODE_DETAIL_MAPPING = {
    "00000001": {
        "functionName": "精煮饭",
        "functionIntro": "耗时比快煮饭长，煮饭的处理方法比较细致。",
        "functionTips": "根据量杯和锅胆内的刻度放入适量的米和水",
        "cookScript": "01100100000001e101000000000011800000010102aa000000000000000000500069030103690000085a020000af006b0401036c0000095a04000119006e0701046f00000a5a0401ffff00700801047100000c5a0401052d0a0f3c0a1e91ff820e01ff05ff78826eff10ff786e02690f0fff826eff691000ff826eff69100069ff55ffdfe1",
    },
    "00000002": {
        "functionName": "快煮饭",
        "functionIntro": "快速煮饭，耗时较短就可以把饭煮好。",
        "functionTips": "根据量杯和锅胆内刻度线放入适量的米和水。",
        "cookScript": "01100200000002e100280000000011800000000002aa0000000000000000008c0069030103690000075a020000f5006b0401036c0000075a02000164006e0700046f0000075a0401ffff0070080004710000075a040100280a063c0d1e91ff820e01ff05ff78826eff10ff786e02690f0cff826eff69100082826eff69100069ff55fff98c",
    },
    "00000003": {
        "functionName": "煮粥",
        "functionIntro": "天生万物，独厚五谷，五谷最养。",
        "functionTips": "各种五谷、粗粮、豆类做成粥，在早晨食用最适宜不过了。",
        "cookScript": "01100300000003e2011e0400010011800000000002aa0000000000000000018255280601003c00000000000001b855280601004600000000000001e056280600004b000000000000ffff57280600005000000000000000280a0082001e914e730e01001e82ff736e0610ff756e02690a1e75826e0469100f75826e0469100069005a006112",
    },
    "00000004": {
        "functionName": "保温",
        "functionIntro": "锁住温度，留住美味。",
        "functionTips": "如果电饭煲需要长时间保温，它会自动调节火力哦",
        "cookScript": "011004000000040c0c001800000100000000000002aa0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000280a003c0d1e914e730e0100058257736e061000786e02690f0075826e02691050826e6e0269100069146e086839",
    },
    "00000005": {
        "functionName": "蒸煮",
        "functionIntro": "煮粥煮饭时可以同时蒸食物",
        "functionTips": "放入适量的水，美味即刻蒸煮出来~",
        "cookScript": "0110030000000566001e0100000a11804000000002aa0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000280a003c001e9155730e0000008278736e001000756e00690a0075826e006910ff756e6e0869100069005a0096b4",
    },
    "00000006": {
        "functionName": "炖汤",
        "functionIntro": "一键就能煮好喝的汤，新手也不怕！",
        "functionTips": "无论是煮海鲜汤还是煮肉汤，您都可以不必顾忌火力大小，也不必担心煮干汤汁，让您轻松享受一碗美味的汤",
        "cookScript": "01100600000006e2011e0400010011800000000002aa0000000000000000018255280601002800000000000001b855280601002800000000000001e0562806000028000000000000ffff57280600002800000000000000280a0082001e914e730e01001e82ff736e0610ff756e02690a1e75826e0469100f75826e0469100069005a00bb28",
    },
    "00000007": {
        "functionName": "蛋糕",
        "functionIntro": "烹饪超美味的蛋糕，口味甜香，老少皆宜。",
        "functionTips": "主要材料有鸡蛋、面粉、牛奶，辅料有白糖、食用油等。按下“蛋糕”静静等待吧~",
        "cookScript": "011003000000078801000100003200001200000002aa0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000280a003c00086278780600001e8278626e041000826e00690fff96626e0469100082826e0069100069005a00a06f",
    },
    "00000008": {
        "functionName": "酸奶",
        "functionIntro": "1000毫升的常温全脂鲜牛奶加上1克酸奶酵母进行酸奶发酵",
        "functionTips": "根据季节、牛奶的使用量和酵母的不同调整发酵时长",
        "cookScript": "011003000000080908000c00060000004000000002aa0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000280a0f260300915573000000008278736e001000756e0028050075826e002810ff75266e0228100069005a000120",
    },
    "00000011": {
        "functionName": "热饭",
        "functionIntro": "热饭效果和现烧的饭几乎一样",
        "functionTips": "水根据烧饭的量适当改变一下。",
        "cookScript": "0110030000001124001e0023001911004000000002aa0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000280a003c000f91416e080000008278736e001000756e00690f0c755a6e0669100082826e0869100069025a04f353",
    },
    "00000014": {
        "functionName": "小米粥",
        "functionIntro": "准备好粥后加水放到电饭煲，盖上盖子静候。",
        "functionTips": "把小米洗净，加水，也可以根据需要加入麦片、冰糖等，一锅小米粥就这样制作完成了。",
        "cookScript": "01100300000014e20100011e002811800000000002aa0000000000000000018255280601003c00000000000001b855280601004600000000000001e056280600004b000000000000ffff57280600005000000000000000280a0082001e914e730e01001e82ff736e0610ff756e02690a1e75826e0469100f75826e0469100069005a003c59",
    },
    "00000015": {
        "functionName": "八宝粥",
        "functionIntro": "准备好米类、豆类后加水放入电饭煲，盖上盖子静候",
        "functionTips": "把杂粮洗净，加水，也可以根据需要加入桂圆、银耳、莲子等，一锅八宝粥就这样制作完成了。",
        "cookScript": "01100300000015e2021e0300020011800000000002aa0000000000000000018255280601003c00000000000001b855280601004600000000000001e056280600004b000000000000ffff57280600005000000000000000280a0082001e914e730e01001e82ff736e0610ff756e02690a1e75826e0469100f75826e0469100069005a00d0a5",
    },
    "00000016": {
        "functionName": "煲仔饭",
        "functionIntro": "简单方便，在家就可以直接做出美味的煲仔饭，比砂锅更快捷。",
        "functionTips": "主料：泰国香米，广式腊肠，辅料：新鲜时蔬，料汁很重要！",
        "cookScript": "01100600000016e101000000000011800200000002aa000000000000000000730069030103690000195a020000af006b0401036c0000195a04000119006e0701046f0000195a0401ffff0070080105710000195a0401002d0a053c0a1e91ff820e01ff05ff78826eff10ff786e02690f0fff826eff691000ff826eff69100069ff7806dca2",
    },
    "00000017": {
        "functionName": "香甜煮",
        "functionIntro": "香甜可口的米饭是这么来的",
        "functionTips": "将米和水配比好倒入电饭煲中，盖上盖子，各时段完美控制温度，保证每一粒米饭受热均匀，香甜可口。 ",
        "cookScript": "01100600000017e1010a0000000011800200000002aa000000000000000000730069030102780000085a020000af006b040102780000085a04000119006e0701027d0000065a0400ffff00700801037d0000065a0400052d0a0f3c0a1e91ff820e01ff05ff78826eff10ff786e02690f1eff826eff691400ff826eff69100069ff55ffb178",
    },
    "00000080": {
        "functionName": "发芽饭",
        "functionIntro": "发芽糙米饭",
        "functionTips": "1、确保糙米带有活性胚芽\n2、糙米提前浸泡12-18小时（冬季延长2小时）\n3、泡糙米的水，不可直接烹饪，需换清水",
        "cookScript": "01100100000080e106000000000011800000000002aa000000000000000000730069030102780000085a020000af006b0401027a0000095a04000119006e0701027b00000a5a0401ffff00700801037d00000c5a040141230af5230a1e91ff820e01ff05ff78826eff10ff786e02690f1eff826eff691000ff826eff69100069ff55ff5787",
    },
}


class CookerProfile:
    """This class can be used to modify and validate an existing cooking profile."""

    def __init__(
        self,
        profile_hex: str,
        index: Optional[int] = None,
        duration: Optional[int] = None,
        schedule: Optional[int] = None,
        auto_keep_warm: Optional[bool] = None,
    ):
        if len(profile_hex) < 5:
            raise ValueError("Invalid profile")
        else:
            self.checksum = bytearray.fromhex(profile_hex)[-2:]
            self.profile_bytes = bytearray.fromhex(profile_hex)[:-2]

            if not self.is_valid():
                raise ValueError("Profile checksum error")
            if index:
                self.set_index(index)
            if duration is not None:
                self.set_duration(duration)
            if schedule is not None:
                self.set_schedule_enabled(True)
                self.set_schedule_duration(schedule)
            if auto_keep_warm is not None:
                self.set_auto_keep_warm_enabled(auto_keep_warm)

    def set_index(self, index: int):
        self.profile_bytes[2] = index
        self.update_checksum()

    def get_index(self) -> int:
        return int(self.profile_bytes[2])

    def get_id(self) -> str:
        return (
            (
                self.profile_bytes[3] << 24
                | self.profile_bytes[4] << 16
                | self.profile_bytes[5] << 8
                | self.profile_bytes[6]
            )
            .to_bytes(4, "big")
            .hex()
        )

    def is_set_duration_allowed(self):
        return (
            self.profile_bytes[10] != self.profile_bytes[12]
            or self.profile_bytes[11] != self.profile_bytes[13]
        )

    def get_duration(self):
        """Get the duration in minutes."""
        return (self.profile_bytes[8] * 60) + self.profile_bytes[9]

    def set_duration(self, minutes):
        """Set the duration in minutes if the profile allows it."""
        if not self.is_set_duration_allowed():
            return

        max_minutes = (self.profile_bytes[10] * 60) + self.profile_bytes[11]
        min_minutes = (self.profile_bytes[12] * 60) + self.profile_bytes[13]

        if minutes < min_minutes or minutes > max_minutes:
            return

        self.profile_bytes[8] = math.floor(minutes / 60)
        self.profile_bytes[9] = minutes % 60

        self.update_checksum()

    def is_schedule_enabled(self):
        return (self.profile_bytes[14] & 0x80) == 0x80

    def set_schedule_enabled(self, enabled):
        if enabled:
            self.profile_bytes[14] |= 0x80
        else:
            self.profile_bytes[14] &= 0x7F

        self.update_checksum()

    def set_schedule_duration(self, duration):
        """Set the schedule time (delay before cooking finished) in minutes of the day."""
        if duration > 1440:
            return

        schedule_flag = self.profile_bytes[14] & 0x80
        self.profile_bytes[14] = math.floor(duration / 60) & 0xFF
        self.profile_bytes[14] |= schedule_flag
        self.profile_bytes[15] = (duration % 60 | self.profile_bytes[15] & 0x80) & 0xFF

        self.update_checksum()

    def is_auto_keep_warm_enabled(self):
        return (self.profile_bytes[15] & 0x80) == 0x80

    def set_auto_keep_warm_enabled(self, enabled):
        if enabled:
            self.profile_bytes[15] |= 0x80
        else:
            self.profile_bytes[15] &= 0x7F

        self.update_checksum()

    def calc_checksum(self):
        import crcmod

        crc = crcmod.mkCrcFun(0x11021, rev=False, initCrc=0x0, xorOut=0x0)(
            self.profile_bytes
        )
        checksum = bytearray(2)
        checksum[0] = (crc >> 8) & 0xFF
        checksum[1] = crc & 0xFF
        return checksum

    def update_checksum(self):
        self.checksum = self.calc_checksum()

    def is_valid(self):
        return (
            len(self.profile_bytes) == 131
            and self.get_id() in COOK_MODE_DETAIL_MAPPING
            and self.checksum == self.calc_checksum()
        )

    def get_profile_hex(self):
        return (self.profile_bytes + self.checksum).hex()


class TemperatureHistory(DeviceStatus):
    def __init__(self, data: str):
        """Container of temperatures recorded every 10-15 seconds while cooking.

        Example values:

        Status waiting:
        0

        2 minutes:
        161515161c242a3031302f2eaa2f2f2e2f

        12 minutes:
        161515161c242a3031302f2eaa2f2f2e2f2e302f2e2d302f2f2e2f2f2f2f343a3f3f3d3e3c3d3c3f3d3d3d3f3d3d3d3d3e3d3e3c3f3f3d3e3d3e3e3d3f3d3c3e3d3d3e3d3f3e3d3f3e3d3c

        32 minutes:
        161515161c242a3031302f2eaa2f2f2e2f2e302f2e2d302f2f2e2f2f2f2f343a3f3f3d3e3c3d3c3f3d3d3d3f3d3d3d3d3e3d3e3c3f3f3d3e3d3e3e3d3f3d3c3e3d3d3e3d3f3e3d3f3e3d3c3f3e3d3c3f3e3d3c3f3f3d3d3e3d3d3f3f3d3d3f3f3e3d3d3d3e3e3d3daa3f3f3f3f3f414446474a4e53575e5c5c5b59585755555353545454555554555555565656575757575858585859595b5b5c5c5c5c5d5daa5d5e5f5f606061

        55 minutes:
        161515161c242a3031302f2eaa2f2f2e2f2e302f2e2d302f2f2e2f2f2f2f343a3f3f3d3e3c3d3c3f3d3d3d3f3d3d3d3d3e3d3e3c3f3f3d3e3d3e3e3d3f3d3c3e3d3d3e3d3f3e3d3f3e3d3c3f3e3d3c3f3e3d3c3f3f3d3d3e3d3d3f3f3d3d3f3f3e3d3d3d3e3e3d3daa3f3f3f3f3f414446474a4e53575e5c5c5b59585755555353545454555554555555565656575757575858585859595b5b5c5c5c5c5d5daa5d5e5f5f60606161616162626263636363646464646464646464646464646464646464646364646464646464646464646464646464646464646464646464646464aa5a59585756555554545453535352525252525151515151

        Data structure:

        Octet 1 (16): First temperature measurement in hex (22 °C)
        Octet 2 (15): Second temperature measurement in hex (21 °C)
        Octet 3 (15): Third temperature measurement in hex (21 °C)
        ...
        """
        if not len(data) % 2:
            self.data = [int(data[i : i + 2], 16) for i in range(0, len(data), 2)]
        else:
            self.data = []

    @property
    def temperatures(self) -> List[int]:
        return self.data

    @property
    def raw(self) -> str:
        return "".join([f"{value:02x}" for value in self.data])

    def __str__(self) -> str:
        return str(self.data)


class CookerStatus(DeviceStatus):
    def __init__(self, data):
        self.data = data

    @property
    def status(self) -> str:
        """Current status."""
        if self.data["status"] in STATUS_MAPPING:
            return STATUS_MAPPING[self.data["status"]]
        return UNKNOWN

    @property
    def menu_index(self) -> int:
        """Selected menu ID"""
        return int(self.data["menu"][0:2], base=16)

    @property
    def menu_id(self) -> str:
        """Selected menu ID"""
        return self.data["menu"][2:10]

    @property
    def menu(self) -> str:
        """Selected menu"""
        return bytes.fromhex(self.data["menu"][10:-2]).decode("gbk")

    @property
    def menu_options(self) -> List[str]:
        """Menu options"""
        options = []
        for i in range(len(self.data["custom_details"]) // 8):
            cook_mode_id = self.data["custom_details"][8 * i : 8 * (i + 1)]
            if cook_mode_id in COOK_MODE_DETAIL_MAPPING:
                options.append(COOK_MODE_DETAIL_MAPPING[cook_mode_id]["functionName"])
            else:
                options.append(UNKNOWN)
        return options

    @property
    def temperature(self) -> Optional[int]:
        """Current temperature.

        Example values: 1e
        """
        return int(self.data["temp"], base=16)

    @property
    def start_time(self) -> datetime:
        """Start time of cooking"""
        return datetime.fromtimestamp(int(self.data["s_time"], 16))

    @property
    def finish_time(self) -> datetime:
        """Finish time of cooking"""
        return datetime.fromtimestamp(int(self.data["f_time"], 16))

    @property
    def duration(self) -> timedelta:
        """Time cost of cooking"""
        return timedelta(
            hours=int(self.data["t_cook"][0:2], 16),
            minutes=int(self.data["t_cook"][2:4], 16),
        )

    @property
    def remaining(self) -> timedelta:
        """Time left of cooking"""
        return timedelta(
            hours=int(self.data["t_left"][0:2], 16),
            minutes=int(self.data["t_left"][2:4], 16),
            seconds=int(self.data["t_left"][4:6], 16),
        )

    @property
    def auto_keep_warm(self) -> bool:
        """Keep warm after cooking?"""
        return self.data["akw"] == "1"

    @property
    def schedule_time(self) -> time:
        """The scheduled time when cooking finished"""
        return time(
            hour=int(self.data["t_pre"][0:2], 16),
            minute=int(self.data["t_pre"][2:4], 16),
        )


class TokitCooker(Device):
    """Main class representing the tokit.cooker.*."""

    _supported_models = [MODEL_TK4001]

    @command(
        default_output=format_output(
            "",
            "Status: {result.status}\n"
            "Menu: {result.menu}\n"
            "Menu Options: {result.menu_options}\n"
            "Cook Duration: {result.duration}\n"
            "Cook Remaining: {result.remaining}\n"
            "Temperature: {result.temperature} °C\n"
            "Auto Keep Warm: {result.auto_keep_warm}\n"
            "Schedule Time: {result.schedule_time}\n"
            "Start time: {result.start_time}\n"
            "Finish time: {result.finish_time}\n",
        )
    )
    def status(self) -> CookerStatus:
        """Retrieve properties."""
        properties = [
            "status",
            "menu",
            "temp",
            "t_cook",
            "t_left",
            "t_pre",
            "t_kw",
            "Phase",
            "cookPhase",
            "e_code",
            "finish_status",
            "taste",
            "ricekind",
            "s_time",
            "f_time",
            "akw",
            "delay_cancel",
            "open_alarm",
            "custom_details",
        ]

        values = self.send("get_prop", properties)

        properties_count = len(properties)
        values_count = len(values)
        if properties_count != values_count:
            _LOGGER.warning(
                "Count (%s) of requested properties does not match the "
                "count (%s) of received values.",
                properties_count,
                values_count,
            )

        return CookerStatus(defaultdict(lambda: None, zip(properties, values)))

    @command(default_output=format_output("", "Temperature history: {result}\n"))
    def get_temperature_history(self) -> TemperatureHistory:
        """Retrieves a temperature history.

        The temperature is only available while cooking. Approx. six data points per
        minute.
        """
        data = self.send("get_temp_history")

        return TemperatureHistory(data[0])

    @command(default_output=format_output("Cooking stopped"))
    def stop(self):
        """Stop cooking, reservation or keeping warm."""
        self.send("cancel_cooking", ["1"])

    @command(
        click.option("--name", type=str),
        click.option("--duration", type=int),
        click.option("--schedule", type=int),
        click.option("--auto_keep_warm", type=bool),
        default_output=format_output("Cooking started"),
    )
    def start(
        self,
        name: Optional[str] = None,
        duration: Optional[int] = None,
        schedule: Optional[int] = None,
        auto_keep_warm: Optional[bool] = None,
    ):
        """Start cooking, reservation or keeping warm."""
        if name:
            if name not in COOK_MODE_NAME_MAPPING.keys():
                raise ValueError(f"Invalid name: {name}")
            cook_profile = CookerProfile(
                COOK_MODE_DETAIL_MAPPING[COOK_MODE_NAME_MAPPING[name]]["cookScript"],
                index=9,
                duration=duration,
                schedule=schedule,
                auto_keep_warm=auto_keep_warm,
            )
        else:
            status: CookerStatus = self.status()
            menu_id = status.menu_id
            cook_profile = CookerProfile(
                COOK_MODE_DETAIL_MAPPING[menu_id]["cookScript"],
                index=9,
            )
            if auto_keep_warm:
                cook_profile.set_auto_keep_warm_enabled(auto_keep_warm)
            else:
                cook_profile.set_auto_keep_warm_enabled(status.auto_keep_warm)
            if duration:
                cook_profile.set_duration(duration)
            else:
                cook_profile.set_duration(int(status.duration.total_seconds() // 60))
            if schedule:
                cook_profile.set_schedule_enabled(True)
                cook_profile.set_schedule_duration(schedule)
            else:
                cook_profile.set_schedule_enabled(False)
        nameCode = (
            COOK_MODE_DETAIL_MAPPING[cook_profile.get_id()]["functionName"]
            .encode("gbk")
            .hex()
            + "00"
        )
        self.send("set_start", [nameCode, cook_profile.get_profile_hex(), "1"])

    @command(
        click.argument("profile", type=str),
        default_output=format_output("Cooking started"),
    )
    def start_by_profile(self, profile):
        """Start cooking, reservation or keeping warm by profile"""
        cook_profile = CookerProfile(profile, index=9)
        nameCode = (
            COOK_MODE_DETAIL_MAPPING[cook_profile.get_id()]["functionName"]
            .encode("gbk")
            .hex()
            + "00"
        )
        self.send("set_start", [nameCode, cook_profile.get_profile_hex(), "1"])

    @command(default_output=format_output("Reset successfully"))
    def reset(self):
        """Factory reset."""
        self.send("set_factory_reset", ["1"])

    @command(
        click.argument("name", type=str),
        click.argument("index", type=int),
        click.option("--duration", type=int),
        click.option("--schedule", type=int),
        click.option("--auto_keep_warm", type=bool),
        default_output=format_output("Set menu successfully"),
    )
    def set_menu(
        self,
        name: str,
        index: int,
        duration: Optional[int] = None,
        schedule: Optional[int] = None,
        auto_keep_warm: Optional[bool] = None,
    ):
        """Set menu."""
        if name not in COOK_MODE_NAME_MAPPING.keys():
            raise ValueError(f"Invalid name: {name}")
        nameCode = name.encode("gbk").hex() + "00"
        cook_profile = CookerProfile(
            COOK_MODE_DETAIL_MAPPING[COOK_MODE_NAME_MAPPING[name]]["cookScript"],
            index,
            duration,
            schedule,
            auto_keep_warm,
        )
        # must send set_menu for 8 times to take effect
        for _ in range(7):
            self.send("set_menu", [nameCode, cook_profile.get_profile_hex(), "0"])
        self.send("set_menu", [nameCode, cook_profile.get_profile_hex(), "1"])

    @command(
        click.argument("profile", type=str),
        default_output=format_output("Set menu successfully"),
    )
    def set_menu_by_profile(self, profile: str):
        """Set menu by cook profile."""
        cook_profile = CookerProfile(profile)
        nameCode = (
            COOK_MODE_DETAIL_MAPPING[cook_profile.get_id()]["functionName"]
            .encode("gbk")
            .hex()
            + "00"
        )
        # must send set_menu for 8 times to take effect
        for _ in range(7):
            self.send("set_menu", [nameCode, cook_profile.get_profile_hex(), "0"])
        self.send("set_menu", [nameCode, cook_profile.get_profile_hex(), "1"])

    @command(
        click.argument("index", type=int),
        default_output=format_output("Delete menu successfully"),
    )
    def delete_menu(self, index: int):
        """Delete menu."""
        if index < 1 or index > 8:
            raise ValueError(f"Invalid index: {index}, should be [1:8]")
        index_str = "0101070" + str(index)
        self.send("set_delete", [index_str, "1"])
