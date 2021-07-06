import enum
import time

import click

from .click_common import EnumType, command
from .device import Device, DeviceStatus


class HourlySystem(enum.Enum):
    TwentyFour = 24
    Twelve = 12


class AlarmType(enum.Enum):
    Alarm = "alarm"
    Reminder = "reminder"
    Timer = "timer"


# TODO names for the tones
class Tone(enum.Enum):
    First = "a1.mp3"
    Second = "a2.mp3"
    Third = "a3.mp3"
    Fourth = "a4.mp3"
    Fifth = "a5.mp3"
    Sixth = "a6.mp3"
    Seventh = "a7.mp3"


class Nightmode(DeviceStatus):
    def __init__(self, data):
        self._enabled = bool(data[0])
        self._start = data[1]
        self._end = data[2]

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end


class RingTone(DeviceStatus):
    def __init__(self, data):
        # {'type': 'reminder', 'ringtone': 'a2.mp3', 'smart_clock': 0}]
        self.type = AlarmType(data["type"])
        self.tone = Tone(data["ringtone"])
        self.smart_clock = data["smart_clock"]


class AlarmClock(Device):
    """Implementation of Xiao AI Smart Alarm Clock.

    Note, this device is not very responsive to the requests, so it may take several
    seconds /tries to get an answer.
    """

    @command()
    def get_config_version(self):
        """
        # values unknown {'result': [4], 'id': 203}
        :return:
        """
        return self.send("get_config_version", ["audio"])

    @command()
    def clock_system(self) -> HourlySystem:
        """Returns either 12 or 24 depending on which system is in use."""
        return HourlySystem(self.send("get_hourly_system")[0])

    @command(click.argument("brightness", type=EnumType(HourlySystem)))
    def set_hourly_system(self, hs: HourlySystem):
        return self.send("set_hourly_system", [hs.value])

    @command()
    def get_button_light(self):
        """Get button's light state."""
        # ['normal', 'mute', 'offline'] or []
        return self.send("get_enabled_key_light")

    @command(click.argument("on", type=bool))
    def set_button_light(self, on):
        """Enable or disable the button light."""
        if on:
            return self.send("enable_key_light") == ["OK"]
        else:
            return self.send("disable_key_light") == ["OK"]

    @command()
    def volume(self) -> int:
        """Return the volume.

        ->  192.168.0.128 data= {"id":251,"method":"set_volume","params":[17]}
        <-  192.168.0.57 data= {"result":["OK"],"id":251}
        """
        return int(self.send("get_volume")[0])

    @command(click.argument("volume", type=int))
    def set_volume(self, volume):
        """Set volume [1,100]."""
        return self.send("set_volume", [volume]) == ["OK"]

    @command(
        click.argument(
            "alarm_type", type=EnumType(AlarmType), default=AlarmType.Alarm.name
        )
    )
    def get_ring(self, alarm_type: AlarmType):
        """Get current ring tone settings."""
        return RingTone(self.send("get_ring", [{"type": alarm_type.value}]).pop())

    @command(
        click.argument("alarm_type", type=EnumType(AlarmType)),
        click.argument("tone", type=EnumType(Tone)),
    )
    def set_ring(self, alarm_type: AlarmType, ring: RingTone):
        """Set alarm tone.

        ->  192.168.0.128 data= {"id":236,"method":"set_ring",
           "params":[{"ringtone":"a1.mp3","smart_clock":"","type":"alarm"}]}
        <-  192.168.0.57 data= {"result":["OK"],"id":236}
        """
        raise NotImplementedError()
        # return self.send("set_ring", ) == ["OK"]

    @command()
    def night_mode(self):
        """Get night mode status.

        ->  192.168.0.128 data= {"id":234,"method":"get_night_mode","params":[]}
        <-  192.168.0.57 data= {"result":[0],"id":234}
        """
        return Nightmode(self.send("get_night_mode"))

    @command()
    def set_night_mode(self):
        """Set the night mode.

        # enable
        ->  192.168.0.128 data= {"id":248,"method":"set_night_mode",
            "params":[1,"21:00","6:00"]}
        <-  192.168.0.57 data= {"result":["OK"],"id":248}

        # disable
        ->  192.168.0.128 data= {"id":249,"method":"set_night_mode",
            "params":[0,"21:00","6:00"]}
        <-  192.168.0.57 data= {"result":["OK"],"id":249}
        """
        raise NotImplementedError()

    @command()
    def near_wakeup(self):
        """Status for near wakeup.

        ->  192.168.0.128 data= {"id":235,"method":"get_near_wakeup_status",
            "params":[]}
        <-  192.168.0.57 data= {"result":["disable"],"id":235}

        # setters
        ->  192.168.0.128 data= {"id":254,"method":"set_near_wakeup_status",
            "params":["enable"]}
        <-  192.168.0.57 data= {"result":["OK"],"id":254}

        ->  192.168.0.128 data= {"id":255,"method":"set_near_wakeup_status",
            "params":["disable"]}
        <-  192.168.0.57 data= {"result":["OK"],"id":255}
        """
        return self.send("get_near_wakeup_status")

    @command()
    def countdown(self):
        """
        ->  192.168.0.128 data= {"id":258,"method":"get_count_down_v2","params":[]}
        """
        return self.send("get_count_down_v2")

    @command()
    def alarmops(self):
        """
        NOTE: the alarm_ops method is the one used to create, query and delete
        all types of alarms (reminders, alarms, countdowns).
        ->  192.168.0.128 data= {"id":263,"method":"alarm_ops",
            "params":{"operation":"create","data":[
                {"type":"alarm","event":"testlabel","reminder":"","smart_clock":0,
                "ringtone":"a2.mp3","volume":100,"circle":"once","status":"on",
                "repeat_ringing":0,"delete_datetime":1564291980000,
                "disable_datetime":"","circle_extra":"",
                "datetime":1564291980000}
                ],"update_datetime":1564205639326}}
        <-  192.168.0.57 data= {"result":[{"id":1,"ack":"OK"}],"id":263}

        # query per index, starts from 0 instead of 1 as the ids it seems
        ->  192.168.0.128 data= {"id":264,"method":"alarm_ops",
            "params":{"operation":"query","req_type":"alarm",
                "update_datetime":1564205639593,"index":0}}
        <-  192.168.0.57 data= {"result":
            [0,[
                {"i":"1","c":"once","d":"2019-07-28T13:33:00+0800","s":"on",
                "n":"testlabel","a":"a2.mp3","dd":1}
               ], "America/New_York"
            ],"id":264}

        # result [code, list of alarms, timezone]
        ->  192.168.0.128 data= {"id":265,"method":"alarm_ops",
            "params":{"operation":"query","index":0,"update_datetime":1564205639596,
                "req_type":"reminder"}}
        <-  192.168.0.57 data= {"result":[0,[],"America/New_York"],"id":265}
        """
        raise NotImplementedError()

    @command(click.argument("url"))
    def start_countdown(self, url):
        """Start countdown timer playing the given media.

        {"id":354,"method":"alarm_ops",
        "params":{"operation":"create","update_datetime":1564206432733,
        "data":[{"type":"timer",
          "background":"http://host.invalid/testfile.mp3",
          "offset":1800,
          "circle":"once",
          "volume":100,
          "datetime":1564208232733}]}}
        """

        current_ts = int(time.time() * 1000)
        payload = {
            "operation": "create",
            "update_datetime": current_ts,
            "data": [
                {
                    "type": "timer",
                    "background": "http://url_here_for_mp3",
                    "offset": 30,
                    "circle": "once",
                    "volume": 30,
                    "datetime": current_ts,
                }
            ],
        }

        return self.send("alarm_ops", payload)

    @command()
    def query(self):
        """
        ->  192.168.0.128 data= {"id":227,"method":"alarm_ops","params":
        {"operation":"query","index":0,"update_datetime":1564205198413,"req_type":"reminder"}}

        """

        payload = {
            "operation": "query",
            "index": 0,
            "update_datetime": int(time.time() * 1000),
            "req_type": "timer",
        }
        return self.send("alarm_ops", payload)

    @command()
    def cancel(self):
        """Cancel alarm of the defined type.

        "params":{"operation":"cancel","update_datetime":1564206332603,"data":[{"type":"timer"}]}}
        """
        import time

        payload = {
            "operation": "pause",
            "update_datetime": int(time.time() * 1000),
            "data": [{"type": "timer"}],
        }
        return self.send("alarm_ops", payload)
