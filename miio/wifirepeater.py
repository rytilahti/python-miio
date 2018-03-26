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


class WifiRepeater(Device):
    """Device class for Xiaomi Mi WiFi Repeater 2."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def status(self) -> WifiRepeaterStatus:
        """Return the associated stations."""
        return WifiRepeaterStatus(self.send("miIO.get_repeater_sta_info", []))

    def configuration(self) -> WifiRepeaterConfiguration:
        """Return the configuration of the accesspoint."""
        return WifiRepeaterConfiguration(
            self.send("miIO.get_repeater_ap_info", []))

    def switch_wifi_explorer(self):
        """Parameters unknown."""
        return self.send("miIO.switch_wifi_explorer", [])

    def switch_wifi_ssid(self):
        """Parameters unknown."""
        return self.send("miIO.switch_wifi_ssid", [])
