from .device import Device
from typing import Any, Dict


class PhilipsEyecare(Device):
    """Main class representing Xiaomi Philips Eyecare Smart Lamp 2."""

    def on(self):
        """Power on."""
        return self.send("set_power", ["on"])

    def off(self):
        """Power off."""
        return self.send("set_power", ["off"])

    def eyecare_on(self):
        """Eyecare on."""
        return self.send("set_eyecare", ["on"])

    def eyecare_off(self):
        """Eyecare off."""
        return self.send("set_eyecare", ["off"])

    def set_bright(self, level: int):
        """Set brightness level."""
        return self.send("set_bright", [level])

    def set_user_scene(self, num: int):
        """Set eyecare user scene."""
        return self.send("set_user_scene", [num])

    def delay_off(self, minutes: int):
        """Set delay off minutes."""
        return self.send("delay_off", [minutes])

    def bl_on(self):
        """Night Light On."""
        return self.send("enable_bl", ["on"])

    def bl_off(self):
        """Night Light Off."""
        return self.send("enable_bl", ["off"])

    def notify_user_on(self):
        """Notify User On."""
        return self.send("set_notifyuser", ["on"])

    def notify_user_off(self):
        """Notify USer Off."""
        return self.send("set_notifyuser", ["off"])

    def amb_on(self):
        """Amblient Light On."""
        return self.send("enable_amb", ["on"])

    def amb_off(self):
        """Ambient Light Off."""
        return self.send("enable_amb", ["off"])

    def set_amb_bright(self, level: int):
        """Set Ambient Light brightness level."""
        return self.send("set_amb_bright", [level])

    def status(self):
        """Retrieve properties."""
        properties = ['power', 'bright', 'notifystatus', 'ambstatus',
                      'ambvalue', 'eyecare', 'scene_num', 'bls',
                      'dvalue', ]
        values = self.send(
            "get_prop",
            properties
        )
        return PhilipsEyecareStatus(dict(zip(properties, values)))


class PhilipsEyecareStatus:
    """Container for status reports from Xiaomi Philips Eyecare Smart Lamp 2"""

    def __init__(self, data: Dict[str, Any]) -> None:
        # ["power","bright","notifystatus","ambstatus","ambvalue","eyecare",
        #    "scene_num","bls","dvalue"]}
        # ["off",5,"off","off",41,"on",3,"on",0]
        self.data = data

    @property
    def power(self) -> str:
        return self.data["power"]

    @property
    def is_on(self) -> bool:
        return self.power == "on"

    @property
    def bright(self) -> int:
        return self.data["bright"]

    @property
    def notifystatus(self) -> str:
        return self.data["notifystatus"]

    @property
    def ambstatus(self) -> str:
        return self.data["ambstatus"]

    @property
    def ambvalue(self) -> int:
        return self.data["ambvalue"]

    @property
    def eyecare(self) -> str:
        return self.data["eyecare"]

    @property
    def scene_num(self) -> str:
        return self.data["scene_num"]

    @property
    def bls(self) -> str:
        return self.data["bls"]

    @property
    def dvalue(self) -> int:
        return self.data["dvalue"]

    def __str__(self) -> str:
        s = "<PhilipsEyecareStatus power=%s, bright=%s, " \
            "notifystatus=%s, ambstatus=%s, ambvalue=%s, " \
            "eyecare=%s, scene_num=%s, bls=%s, " \
            "dvalue=%s >" % \
            (self.power, self.bright,
             self.notifystatus, self.ambstatus, self.ambvalue,
             self.eyecare, self.scene_num, self.bls, self.dvalue)
        return s
