import logging
from collections import defaultdict
from dataclasses import dataclass, field, replace
from datetime import date, datetime, time, timedelta, timezone
from typing import Dict, List, Optional

import click

from miio import Device
from miio.click_common import command, format_output
from miio.exceptions import DeviceException

from .status import PetFeederStatus

_LOGGER = logging.getLogger(__name__)

MODEL_MMGG_FEEDER_PETFEEDER = "mmgg.feeder.petfeeder"

SUPPORTED_MODELS: List[str] = [MODEL_MMGG_FEEDER_PETFEEDER]

AVAILABLE_PROPERTIES: Dict[str, List[str]] = {
    MODEL_MMGG_FEEDER_PETFEEDER: [
        "food_level",
        "feed_plan",
        "food_outlet",
        "dispensed_today",  # Not populated
        "clean_days_left",
        "food_storage_lid",
        "desiccant_days_left",
        "dispense_portion",  # Not populated
        "wifi_led",
        "button_lock",
        "country_code",
    ],
}

OK = ["ok"]


class PetFeederException(DeviceException):
    pass


class PetFeederNoFreeSlots(ValueError):
    pass


class PetFeederInvalidSlot(ValueError):
    pass


@dataclass
class FeedPlan:
    """Feedplan Class."""

    _device_tz = timezone(timedelta(hours=8))

    slot: int
    hour: int
    minute: int
    units: int
    tz: Optional[timezone] = _device_tz
    datetime: datetime = field(init=False)
    enabled: bool = field(init=False)

    def __post_init__(self):
        self.enabled = any(
            value != 255 for value in [self.hour, self.minute, self.units]
        )
        self.datetime = datetime.combine(
            date.today(),
            time(self.hour, self.minute) if self.enabled else time.min,
            tzinfo=self.tz if self.tz else self._device_tz,
        )
        if self.tz != self._device_tz:
            self.datetime = self.datetime.astimezone(self._device_tz)

    def format(self):
        return f"{self.slot:02d}{self.datetime.strftime('%H%M')}{self.units:02d}"


class PetFeeder(Device):
    """Main class representing the Pet Feeder / Smart Pet Food Dispenser."""

    _supported_models = SUPPORTED_MODELS

    _local_tz = datetime.now().astimezone().tzinfo

    @command(
        default_output=format_output(
            "",
            "Food level: {result.food_level.name}\n"
            "Feed plan: {result.feed_plan}\n"
            "Food outlet: {result.food_outlet.name}\n"
            "Food storage lid: {result.food_storage_lid.name}\n"
            "Days until cleaning required: {result.clean_days_left.days} day(s)\n"
            "Days until desiccant replacement: {result.desiccant_days_left.days} day(s)\n"
            "WiFi status led: {result.wifi_led}\n"
            "Dispense button lock: {result.button_lock}\n",
        )
    )
    def status(self) -> PetFeederStatus:
        """Retrieve properties.

        :return: Device attributes
        :rtype: PetFeederStatus
        """
        properties = AVAILABLE_PROPERTIES.get(
            self.model, AVAILABLE_PROPERTIES[MODEL_MMGG_FEEDER_PETFEEDER]
        )
        values = self.send("getprops")
        return PetFeederStatus(defaultdict(lambda: None, zip(properties, values)))

    @command(
        click.argument("units", type=int),
        default_output=format_output("Dispensing {units} unit(s)"),
    )
    def dispense_food(self, units: int):
        """Dispense food.

        Manually dispense food.

        :param int units: Number of units to dispense (1 unit ~= 5g)
        :return: MiIO response
        :rtype: bool
        """
        return self.send("outfood", [units]) == OK

    @command(default_output=format_output("Resetting desiccant time left"))
    def reset_desiccant_left(self) -> bool:
        """Reset desiccant time.

        Reset the desiccant life counter (30 days)

        :return: MiIO response
        :rtype: bool
        """
        date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        return self.send("resetdryer", [date]) == OK

    @command(
        click.argument("state", type=int),
        default_output=format_output(
            lambda state: "Turning on WiFi led" if state else "Turning off WiFi led"
        ),
    )
    def set_wifi_led(self, state: bool):
        """Set wifi led.

        Enable / Disable the wifi status led.

        :param bool state: On / Off
        :return: MiIO response
        :rtype: bool
        """
        return self.send("wifiledon", [int(state)]) == OK

    @command(
        click.argument("state", type=int),
        default_output=format_output(
            lambda state: "Locking dispense button"
            if state
            else "Unlocking dispense button"
        ),
    )
    def set_button_lock(self, state: bool):
        """Set button lock.

        Lock / Unlock the manual dispense button.

        :param bool state: Unlocked / Locked
        :return: MiIO response
        :rtype: bool
        """
        return self.send("keylock", [int(state) ^ 1]) == OK

    @command(
        click.argument("state", type=int),
        default_output=format_output(
            lambda state: "Enabling automatic feeding schedule"
            if state
            else "Disabling automatic feeding schedule"
        ),
    )
    def set_feed_state(self, state: bool):
        """Set feed state.

        Enable / Disable the automatic feeding schedule.

        :param bool state: Off / On
        :return: MiIO response
        :rtype: bool
        """
        return self.send("stopfeed", [int(state)]) == OK

    @command(
        default_output=format_output(
            "",
            lambda result: "".join(
                (
                    f"Slot: {plan.slot:02d} "
                    f"Time: {plan.datetime.astimezone(PetFeeder._local_tz).strftime('%H:%M')} "
                    f"Units: {plan.units}\n"
                )
                for plan in result
                if plan.enabled
            ),
        ),
    )
    def get_feed_plans(self) -> List[FeedPlan]:
        """Get feed plans.

        Return all feeding plans.

        return: List of FeedPlan objects
        rtype: list
        raises PetFeederException: if the number of elements returned is wrong
        """
        feed_plans = []
        for i in (1, 2):
            plans = self.send(f"getfeedplan{i}", [])
            if len(plans) < 25:
                raise PetFeederException("Error getting feed plans")
            for plan in [plans[i : i + 4] for i in range(0, len(plans), 5)]:
                feed_plans.append(FeedPlan(*plan))
        return feed_plans

    @command(
        click.option("-h", "--hour", type=int),
        click.option("-m", "--minute", type=int),
        click.option("-u", "--units", type=int),
        default_output=format_output(
            "Added feed plan {hour:02d}:{minute:02d} - {units} units"
        ),
    )
    def add_feed_plan(self, hour: int, minute: int, units: int) -> bool:
        """Add Feed Plan.

        Add a feeding plan.
        Hours in local tz.

        :param int hour: Hour
        :param int minute: Minute
        :param int units: Number of units to dispense (1 unit ~= 5g)
        :return: MiIO response
        :rtype: bool
        :raises PetFeederNoFreeSlots: if there are no unused feed plan slots
        :raises ValueError: if units < 0 > 30
        """
        if units < 0 or units > 30:
            raise ValueError("Units must be between 1-30")
        try:
            slot = next(plan for plan in self.get_feed_plans() if not plan.enabled)
        except StopIteration:
            raise PetFeederNoFreeSlots("All feed plan slots in use")
        plan = replace(slot, hour=hour, minute=minute, units=units, tz=self._local_tz)
        return self.send("feedListAdd", [plan.format()]) == OK

    @command(
        click.option("-s", "--slot", type=int, required=True),
        click.option("-h", "--hour", type=int),
        click.option("-m", "--minute", type=int),
        click.option("-u", "--units", type=int),
        default_output=format_output("Updated feed plan {slot}"),
    )
    def edit_feed_plan(self, slot: int, hour: int, minute: int, units: int) -> bool:
        """Edit Feed Plan.

        Edit a pre-existing feeding plan.

        :param int slot: Feed plan slot
        :keyword int hour: Hour
        :keyword int minute: Minute
        :keyword int units: Number of units to dispense (1 unit ~= 5g)
        :return: MiIO response
        :rtype: bool
        :raises PetFeederInvalidSlot: if slot not found
        :raises ValueError: if units < 0 > 30
        """
        try:
            plan = next(plan for plan in self.get_feed_plans() if plan.slot == slot)
        except StopIteration:
            raise PetFeederInvalidSlot("Invalid feed plan slot")
        if (units is not None) and (units < 0 or units > 30):
            raise ValueError("Units must be between 1-30")
        new_plan = replace(
            plan,
            hour=hour if hour else plan.hour,
            minute=minute if minute else plan.minute,
            units=units if units else plan.units,
            tz=self._local_tz if hour else None,
        )
        return self.send("feedListEdit", [new_plan.format()]) == OK

    @command(
        click.option("-s", "--slot", type=int, required=True),
        default_output=format_output("Deleting feed plan {slot}"),
    )
    def del_feed_plan(self, slot: int) -> bool:
        """Delete Feed Plan.

        Delete a feeding plan.

        :param int slot: Feed plan slot
        :return: MiIO response
        :rtype: bool
        :raises PetFeederInvalidSlot: if slot not found
        """
        try:
            plan = next(plan for plan in self.get_feed_plans() if plan.slot == slot)
        except StopIteration:
            raise PetFeederInvalidSlot()
        return self.send("feedListDel", [plan.format()]) == OK
