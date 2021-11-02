from typing import Any, Dict
import enum
import logging

import click

from .click_common import EnumType, command, format_output
from .exceptions import DeviceException
from .miot_device import MiotDevice, DeviceStatus

_LOGGER = logging.getLogger(__name__)

MODEL_MMGG_PET_WATERER_S1 = 'mmgg.pet_waterer.s1'

SUPPORTED_MODELS = [
    MODEL_MMGG_PET_WATERER_S1,
]

_MAPPING = {
    # https://home.miot-spec.com/spec/mmgg.pet_waterer.s1
    'cotton_left_time': {'siid': 5, 'piid': 1},
    'reset_cotton_life': {'siid': 5, 'aiid': 1},
    'reset_clean_time': {'siid': 6, 'aiid': 1},
    'fault': {'siid': 2, 'piid': 1},
    'filter_left_time': {'siid': 3, 'piid': 1},
    'indicator_light': {'siid': 4, 'piid': 1},
    'lid_up_flag': {'siid': 7, 'piid': 4},
    'location': {'siid': 9, 'piid': 2},
    'mode': {'siid': 2, 'piid': 3},
    'no_water_flag': {'siid': 7, 'piid': 1},
    'no_water_time': {'siid': 7, 'piid': 2},
    'on': {'siid': 2, 'piid': 2},
    'pump_block_flag': {'siid': 7, 'piid': 3},
    'remain_clean_time': {'siid': 6, 'piid': 1},
    'reset_filter_life': {'siid': 3, 'aiid': 1},
    'reset_device': {'siid': 8, 'aiid': 1},
    'timezone': {'siid': 9, 'piid': 1},
}


class OperatingMode(enum.Enum):
    common = 1
    smart = 2


class PetWaterDispenserException(DeviceException):
    pass


class PetWaterDispenserStatus(DeviceStatus):
    '''Container for status reports from the Pet Water Dispenser'''

    def __init__(self, data: Dict[str, Any]) -> None:
        '''Pet Waterer / Pet Drinking Fountain / Smart Pet Water Dispenser (mmgg.pet_waterer.s1)'''
        self.data = data

    @property
    def filter_left_time(self) -> int:
        '''Filter life time remaining in days'''
        return self.data['filter_left_time']

    @property
    def power(self) -> str:
        if self.data['on']:
            return 'on'
        return 'off'

    @property
    def is_on(self) -> bool:
        '''True if device is on'''
        return self.data['on']

    @property
    def mode(self) -> str:
        '''OperatingMode'''
        return OperatingMode(self.data['mode']).name

    @property
    def indicator_light_enabled(self) -> bool:
        '''True if enabled'''
        return self.data['indicator_light']

    @property
    def cotton_left_time(self) -> int:
        return self.data['cotton_left_time']

    @property
    def days_before_cleaning(self) -> int:
        return self.data['remain_clean_time']

    @property
    def no_water(self) -> bool:
        '''True if there is no water left'''
        if self.data['no_water_flag']:
            return False
        return True

    @property
    def minutes_without_water(self) -> int:
        return self.data['no_water_time']

    @property
    def pump_is_blocked(self) -> bool:
        '''True if pump is blocked'''
        return self.data['pump_block_flag']

    @property
    def lid_is_up(self) -> bool:
        '''True if lid is up'''
        return self.data['lid_up_flag']

    @property
    def timezone(self) -> int:
        return self.data['timezone']

    @property
    def location(self) -> str:
        return self.data['location']

    @property
    def error_detected(self) -> bool:
        '''True if fault detected'''
        return self.data['fault'] > 0


class PetWaterDispenser(MiotDevice):
    '''Main class representing the pet water dispenser.'''

    mapping = _MAPPING

    @command(
        default_output=format_output(
            '',
            'Cotton filter live: {result.cotton_left_time} day(s) left\n'
            'Days before cleaning: {result.days_before_cleaning} day(s)\n'
            'Error detected: {result.error_detected}\n'
            'Filter live: {result.filter_left_time} day(s) left\n'
            'Indicator light enabled: {result.indicator_light_enabled}\n'
            'Lid is up: {result.lid_is_up}\n'
            'Location: {result.location}\n'
            'Mode: {result.mode}\n'
            'Minutes without water: {result.minutes_without_water} minute(s)\n'
            'No water: {result.no_water}\n'
            'Power: {result.power}\n'
            'Pump is blocked: {result.pump_is_blocked}\n'
            'Timezone: {result.timezone}\n'
        )
    )
    def status(self) -> PetWaterDispenserStatus:
        '''Retrieve properties.'''
        return PetWaterDispenserStatus(
            {
                prop['did']: prop['value'] if prop['code'] == 0 else None
                for prop in self.get_properties_for_mapping()
            }
        )

    @command(default_output=format_output('Powering off ...'))
    def off(self) -> Any:
        '''Power off.'''
        status = self.status()
        if not status.is_on:
            return 'Already off'
        resp = self.set_property('on', False)
        if resp[0]['code'] != 0:
            raise PetWaterDispenserException(resp)
        return 'ok'

    @command(default_output=format_output('Powering on ...'))
    def on(self) -> str:
        '''Power on.'''
        status = self.status()
        if status.is_on:
            return 'Already on'
        resp = self.set_property('on', True)
        if resp[0]['code'] != 0:
            raise PetWaterDispenserException(resp)
        return 'ok'

    @command(default_output=format_output('Disabling indicator light ...'))
    def disable_indicator_light(self) -> str:
        '''Turn off idicator light.'''
        status = self.status()
        if not status.indicator_light_enabled:
            return 'Already disabled'
        resp = self.set_property('indicator_light', False)
        if resp[0]['code'] != 0:
            raise PetWaterDispenserException(resp)
        return 'OK'

    @command(default_output=format_output('Enabling indicator light ...'))
    def enable_indicator_light(self) -> str:
        '''Turn off idicator light.'''
        status = self.status()
        if status.indicator_light_enabled:
            return 'Already enabled'
        resp = self.set_property('indicator_light', True)
        if resp[0]['code'] != 0:
            raise PetWaterDispenserException(resp)
        return 'OK'

    @command(
        click.argument('mode', type=EnumType(OperatingMode)),
        default_output=format_output('Changing mode to "{mode.name}" ...')
    )
    def set_mode(self, mode: OperatingMode) -> str:
        '''Switch operation mode.'''
        status = self.status()
        if status.mode == mode.value:
            return f'Already set to "{status.mode}"'
        resp = self.set_property('mode', mode.value)
        if resp[0]['code'] != 0:
            raise PetWaterDispenserException(resp)
        return 'OK'

    @command(default_output=format_output('Resetting filter ...'))
    def reset_filter(self) -> str:
        '''Reset filter life counter.'''
        resp = self.call_action('reset_filter_life')
        if resp[0]['code'] != 0:
            raise PetWaterDispenserException(resp)
        return 'OK'

    @command(default_output=format_output('Resetting cotton filter ...'))
    def reset_cotton_filter(self) -> str:
        '''Reset cotton filter life counter.'''
        resp = self.call_action('reset_cotton_life')
        if resp[0]['code'] != 0:
            raise PetWaterDispenserException(resp)
        return 'OK'

    @command(default_output=format_output('Resetting cleaning time ...'))
    def reset_cleaning_time(self) -> str:
        '''Reset cleaning time counter.'''
        resp = self.call_action('reset_clean_time')
        if resp[0]['code'] != 0:
            raise PetWaterDispenserException(resp)
        return 'OK'

    @command(default_output=format_output('Resetting device ...'))
    def reset(self) -> str:
        '''Reset device.'''
        resp = self.call_action('reset_device')
        if resp[0]['code'] != 0:
            raise PetWaterDispenserException(resp)
        return 'OK'

    @command(
        click.argument('timezone', type=click.IntRange(-12, 12)),
        default_output=format_output('Changing timezone to "{timezone}" ...')
    )
    def set_timezone(self, timezone: int) -> str:
        '''Change timezone.'''
        status = self.status()
        if status.timezone == timezone:
            return f'Already set to "{status.timezone}"'
        resp = self.set_property('timezone', timezone)
        if resp[0]['code'] != 0:
            raise PetWaterDispenserException(resp)
        return 'OK'

    @command(
        click.argument('location', type=str),
        default_output=format_output('Changing location to "{location}" ...')
    )
    def set_location(self, location: str) -> str:
        '''Change location.'''
        status = self.status()
        if status.location == location:
            return f'Already set to "{status.location}"'
        resp = self.set_property('location', location)
        if resp[0]['code'] != 0:
            raise PetWaterDispenserException(resp)
        return 'OK'
