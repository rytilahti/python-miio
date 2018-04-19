from unittest import TestCase

import pytest

from miio import WifiRepeater
from miio.wifirepeater import WifiRepeaterConfiguration, WifiRepeaterStatus


class DummyWifiRepeater(WifiRepeater):
    def __init__(self, *args, **kwargs):
        self.state = {
            'sta': {'count': 2, 'access_policy': 0},
            'mat': [
                {'mac': 'aa:aa:aa:aa:aa:aa', 'ip': '192.168.1.133',
                 'last_time': 54371873},
                {'mac': 'bb:bb:bb:bb:bb:bb', 'ip': '192.168.1.156',
                 'last_time': 54371496}
            ],
            'access_list': {'mac': ''}
        }
        self.config = {'ssid': 'SSID', 'pwd': 'PWD', 'hidden': 0}
        self.device_info = {
            'life': 543452, 'cfg_time': 543452,
            'token': 'ffffffffffffffffffffffffffffffff',
            'fw_ver': '2.2.14', 'hw_ver': 'R02',
            'uid': 1583412143, 'api_level': 2,
            'mcu_fw_ver': '1000', 'wifi_fw_ver': '1.0.0',
            'mac': 'FF:FF:FF:FF:FF:FF',
            'model': 'xiaomi.repeater.v2',
            'ap': {'rssi': -63, 'ssid': 'SSID',
                   'bssid': 'EE:EE:EE:EE:EE:EE',
                   'rx': 136695922, 'tx': 1779521233},
            'sta': {'count': 2, 'ssid': 'REPEATER-SSID',
                    'hidden': 0,
                    'assoclist': 'cc:cc:cc:cc:cc:cc;bb:bb:bb:bb:bb:bb;'},
            'netif': {'localIp': '192.168.1.170',
                      'mask': '255.255.255.0',
                      'gw': '192.168.1.1'},
            'desc': {'wifi_explorer': 1,
                     'sn': '14923 / 20191356', 'color': 101,
                     'channel': 'release'}
        }

        self.return_values = {
            'miIO.get_repeater_sta_info': self._get_state,
            'miIO.get_repeater_ap_info': self._get_configuration,
            'miIO.switch_wifi_explorer': self._set_wifi_explorer,
            'miIO.switch_wifi_ssid': self._set_configuration,
            'miIO.info': self._get_info,
        }
        self.start_state = self.state.copy()
        self.start_config = self.config.copy()
        self.start_device_info = self.device_info.copy()

    def send(self, command: str, parameters=None, retry_count=3):
        """Overridden send() to return values from `self.return_values`."""
        return self.return_values[command](parameters)

    def _reset_state(self):
        """Revert back to the original state."""
        self.state = self.start_state.copy()
        self.config = self.start_config.copy()
        self.device_info = self.start_device_info.copy()

    def _get_state(self, param):
        return self.state

    def _get_configuration(self, param):
        return self.config

    def _get_info(self, param):
        return self.device_info

    def _set_wifi_explorer(self, data):
        self.device_info['desc']['wifi_explorer'] = data[0]['wifi_explorer']

    def _set_configuration(self, data):
        self.config = {
            'ssid': data[0]['ssid'],
            'pwd': data[0]['pwd'],
            'hidden': data[0]['hidden']
        }

        self.device_info['desc']['wifi_explorer'] = data[0]['wifi_explorer']
        return True


@pytest.fixture(scope="class")
def wifirepeater(request):
    request.cls.device = DummyWifiRepeater()
    # TODO add ability to test on a real device


@pytest.mark.usefixtures("wifirepeater")
class TestWifiRepeater(TestCase):
    def state(self):
        return self.device.status()

    def configuration(self):
        return self.device.configuration()

    def info(self):
        return self.device.info()

    def wifi_roaming(self):
        return self.device.wifi_roaming()

    def rssi_accesspoint(self):
        return self.device.rssi_accesspoint()

    def test_status(self):
        self.device._reset_state()

        assert repr(self.state()) == repr(WifiRepeaterStatus(self.device.start_state))

        assert self.state().access_policy == self.device.start_state['sta']['access_policy']
        assert self.state().associated_stations == self.device.start_state['mat']

    def test_set_wifi_roaming(self):
        self.device.set_wifi_roaming(True)
        assert self.wifi_roaming() is True

        self.device.set_wifi_roaming(False)
        assert self.wifi_roaming() is False

    def test_configuration(self):
        self.device._reset_state()

        assert repr(self.configuration()) == repr(WifiRepeaterConfiguration(self.device.start_config))

        assert self.configuration().ssid == self.device.start_config['ssid']
        assert self.configuration().password == self.device.start_config['pwd']
        assert self.configuration().ssid_hidden is (self.device.start_config['hidden'] == 1)

    def test_set_configuration(self):
        def configuration():
            return self.device.configuration()

        dummy_configuration = {
            'ssid': 'SSID2',
            'password': 'PASSWORD2',
            'hidden': True,
        }

        self.device.set_configuration(
            dummy_configuration['ssid'],
            dummy_configuration['password'],
            dummy_configuration['hidden'])
        assert configuration().ssid == dummy_configuration['ssid']
        assert configuration().password == dummy_configuration['password']
        assert configuration().ssid_hidden is dummy_configuration['hidden']

    def test_rssi_accesspoint(self):
        self.device._reset_state()

        assert self.rssi_accesspoint() is self.device.start_device_info['ap']['rssi']
