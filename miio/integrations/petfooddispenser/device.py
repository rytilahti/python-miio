import logging
from typing import Any, Dict, List

from collections import defaultdict
import click

from miio.click_common import EnumType, command, format_output
from miio.device import Device


from .status import PetFoodDispenserStatus

_LOGGER = logging.getLogger(__name__)

MODEL_MMGG_FEEDER_PETFEEDER = "mmgg.feeder.petfeeder"

SUPPORTED_MODELS: List[str] = [MODEL_MMGG_FEEDER_PETFEEDER]

AVAILABLE_PROPERTIES: Dict[str, List[str]] = {
    MODEL_MMGG_FEEDER_PETFEEDER: [
        "food_status",
        "feed_plan",
        "door_status",
        "feed_today",
        "clean_days",
        "power_status",
        "dryer_days",
        "food_portion",
        "wifi_led",
        "key_lock",
        "country_code",
    ],
}

class PetFoodDispenser(Device):
    """Main class representing the Pet Feeder / Smart Pet Food Dispenser. """

    _supported_models = SUPPORTED_MODELS

    @command(
        default_output=format_output(
            "",
            "Power source: {result.power_status}\n"
            "Food level: {result.food_status}\n"
            "Automatic feeding: {result.feed_plan}\n"
            "Food bin lid: {result.door_status}\n"
            "Dispense button lock: {result.key_lock}\n"
            "Days until clean: {result.clean_days}\n"
            "Dessicant life: {result.dryer_days}\n"
            "WiFi LED: {result.wifi_led}\n",
        )
    )
    def status(self) -> PetFoodDispenserStatus:
        """Retrieve properties."""
        properties = AVAILABLE_PROPERTIES.get(
            self.model, AVAILABLE_PROPERTIES[MODEL_MMGG_FEEDER_PETFEEDER]
        )
        values = self.send('getprops')
        return PetFoodDispenserStatus(defaultdict(lambda: None, zip(properties, values)))

    @command(
        click.argument("amount", type=int),
        default_output=format_output("Dispensing {amount} units)"),
    )
    def dispense_food(self, amount: int):
        """Dispense food.
        :param amount: in units (1 unit ~= 5g)
        """
        return self.send("outfood", [amount])

    @command(default_output=format_output("Resetting clean time"))
    def reset_clean_time(self) -> bool:
        """Reset clean time."""
        return self.send("resetclean")

    @command(default_output=format_output("Resetting dryer time"))
    def reset_dryer_time(self) -> bool:
        """Reset dryer time."""
        return self.send("resetdryer")

    @command(
        click.argument("state", type=int),
        default_output=format_output(
            lambda state: "Turning on WiFi LED" if state else "Turning off WiFi LED"
        ),
    )
    def set_wifi_led(self, state: int):
        """Enable / Disable the wifi status led."""
        return self.send("wifiledon", [state])

    @command(
        click.argument("state", type=int),
        default_output=format_output(
            lambda state: "Enabling key lock for dispense button" if state else "Disabling key lock for dispense button"
        ),
    )
    def set_key_lock(self, state: int):
        """Enable / Disable the key lock for the manual dispense button."""
        return self.send("keylock", [state ^ 1])

    @command(
        click.argument("state", type=int),
        default_output=format_output(
            lambda state: "Enabling automatic feeding schedule" if state else "Disabling automatic feeding schedule"
        ),
    )
    def set_feed_state(self, state: int):
        """Enable / Disable the automatic feeding schedule."""
        return self.send("stopfeed", [state])


