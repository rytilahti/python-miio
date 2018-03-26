import logging
from .device import Device

_LOGGER = logging.getLogger(__name__)


class WifiRepeaterStatus:
    def __init__(self, data):
        """
        Response of a xiaomi.repeater.v2:

        {
          'sta': {'count': 2, 'access_policy': 0},
          'mat': [
            {'mac': 'aa:aa:aa:aa:aa:aa', 'ip': '192.168.1.133', 'last_time': 54371873},
            {'mac': 'bb:bb:bb:bb:bb:bb', 'ip': '192.168.1.156', 'last_time': 54371496}
          ],
          'access_list': {'mac': ''}
        }
        """
        self.data = data

    @property
    def access_policy(self) -> int:
        """Access policy of the associated stations."""
        return self.data['sta']['access_policy']

    @property
    def associated_stations(self) -> dict:
        """List of associated stations."""
        return self.data['mat']

    def __repr__(self) -> str:
        s = "<WifiRepeaterStatus access_policy=%s, " \
            "associated_stations=%s>" % \
            (self.access_policy,
             len(self.associated_stations))
        return s


class WifiRepeaterConfiguration:
    def __init__(self, data):
        """
        Response of a xiaomi.repeater.v2:

        {'ssid': 'SSID', 'pwd': 'PWD', 'hidden': 0}
        """
        self.data = data

    @property
    def ssid(self) -> str:
        return self.data['ssid']

    @property
    def password(self) -> str:
        return self.data['pwd']

    @property
    def ssid_hidden(self) -> bool:
        return self.data['hidden'] == 1

    def __repr__(self) -> str:
        s = "<WifiRepeaterConfiguration ssid=%s, " \
            "password=%s, " \
            "ssid_hidden=%s>" % \
            (self.ssid,
             self.password,
             self.ssid_hidden)
        return s


class WifiRepeater(Device):
    """Device class for Xiaomi Mi WiFi Repeater 2."""
    def status(self) -> WifiRepeaterStatus:
        """Return the associated stations."""
        return WifiRepeaterStatus(self.send("miIO.get_repeater_sta_info", []))

    def configuration(self) -> WifiRepeaterConfiguration:
        """Return the configuration of the accesspoint."""
        return WifiRepeaterConfiguration(
            self.send("miIO.get_repeater_ap_info", []))

    def set_wifi_roaming(self, wifi_roaming: bool):
        """Turn the WiFi roaming on/off."""
        return self.send("miIO.switch_wifi_explorer", [{
            'wifi_explorer': int(wifi_roaming)
        }])

    def set_configuration(self, ssid: str, password: str, hidden: bool = False,
                          wifi_roaming: bool = False):
        """Update the configuration of the accesspoint."""
        return self.send("miIO.switch_wifi_ssid", [{
            'ssid': ssid,
            'pwd': password,
            'hidden': int(hidden),
            'wifi_explorer': int(wifi_roaming)
        }])
