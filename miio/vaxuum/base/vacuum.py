import click

from miio.click_common import (
    command,
)
from .containers import (
    FanSpeed,
    VacuumStatus,
    ConsumableStatus,
    FanSpeed,
)
from typing import Union


class BaseVacuum:
    """ Base Vacuum Interface """
    @command()
    def start(self):
        """Start cleaning"""
        raise NotImplementedError

    # spot cleaning

    @command()
    def stop(self):
        """Stop cleaning"""
        raise NotImplementedError

    @command()
    def pause(self):
        """Pause cleaning"""
        raise NotImplementedError

    @command()
    def resume(self):
        """Resume current cleaning process or start new process"""
        raise NotImplementedError

    # manual_start
    # manual_stop
    # manual_control (maybe without once)

    @command()
    def return_to_dock(self):
        """Stop cleaning and return to dock."""
        raise NotImplementedError

    @command()
    def status(self) -> VacuumStatus:
        """Return current status of Vacuum"""
        raise NotImplementedError

    @command()
    def consumable_status(self) -> ConsumableStatus:
        """ Get status of consumables"""
        raise NotImplementedError

    # reset_consumable
    # map management
    # nogo zones, barriers

    # clean_history
    # clean_details

    @command()
    def find(self):
        """Locate the vacuum """
        raise NotImplementedError

    # timers
    # do not disturb

    # get speed via state

    @command(click.argument("speed", type=int))
    def set_fan_speed(self, speed: Union[int, FanSpeed]):
        """Set fan speed
        See .status for getting current speed

        :param speed: pass int for raw model-dependent value, or VacuumSpeed for common preset
        """
        _ = speed
        raise NotImplementedError

    # mopping/water related features
    # stats
