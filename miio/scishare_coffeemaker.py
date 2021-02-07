import logging
from enum import IntEnum

import click

from .click_common import command, format_output
from .device import Device

_LOGGER = logging.getLogger(__name__)

MODEL = "scishare.coffee.s1102"


class Status(IntEnum):
    Unknown = -1
    Off = 1
    On = 2
    SelfCheck = 3
    StopPreheat = 4
    CoffeeReady = 5
    StopDescaling = 6
    Standby = 7
    Preheating = 8

    Brewing = 201
    NoWater = 203


class ScishareCoffee(Device):
    """Main class for Scishare coffee maker (scishare.coffee.s1102)."""

    @command()
    def status(self) -> int:
        """Device status."""
        status_code = self.send("Query_Machine_Status")[1]
        try:
            return Status(status_code)
        except ValueError:
            _LOGGER.warning(
                "Status code unknown, please report the state of the machine for code %s",
                status_code,
            )
            return Status.Unknown

    @command(
        click.argument("temperature", type=int),
        default_output=format_output("Setting preheat to {temperature}"),
    )
    def preheat(self, temperature: int):
        """Pre-heat to given temperature."""
        return self.send("Boiler_Preheating_Set", [temperature])

    @command(default_output=format_output("Stopping pre-heating"))
    def stop_preheat(self) -> bool:
        """Stop pre-heating."""
        return self.send("Stop_Boiler_Preheat")[0] == "ok"

    @command()
    def cancel_alarm(self) -> bool:
        """Unknown."""
        raise NotImplementedError()
        return self.send("Cancel_Work_Alarm")[0] == "ok"

    @command(
        click.argument("amount", type=int),
        click.argument("temperature", type=int),
        default_output=format_output("Boiling {amount} ml water ({temperature}C)"),
    )
    def boil_water(self, amount: int, temperature: int) -> bool:
        """Boil water.

        :param amount: in milliliters
        :param temperature: in degrees
        """
        return self.send("Hot_Wate", [amount, temperature])[0] == "ok"

    @command(
        click.argument("amount", type=int),
        click.argument("temperature", type=int),
        default_output=format_output("Brewing {amount} ml espresso ({temperature}C)"),
    )
    def brew_espresso(self, amount: int, temperature: int):
        """Brew espresso.

        :param amount: in milliliters
        :param temperature: in degrees
        """
        return self.send("Espresso_Coffee", [amount, temperature])[0] == "ok"

    @command(
        click.argument("water_amount", type=int),
        click.argument("water_temperature", type=int),
        click.argument("coffee_amount", type=int),
        click.argument("coffee_temperature", type=int),
        default_output=format_output(
            "Brewing americano using {water_amount} ({water_temperature}C) water and {coffee_amount} ml ({coffee_temperature}C) coffee"
        ),
    )
    def brew_americano(
        self,
        water_amount: int,
        water_temperature: int,
        coffee_amount: int,
        coffee_temperature: int,
    ) -> bool:
        """Brew americano.

        :param water_amount: water in milliliters
        :param water_temperature: water temperature
        :param coffee_amount: coffee amount in milliliters
        :param coffee_temperature: coffee temperature
        """
        return (
            self.send(
                "Americano_Coffee",
                [water_amount, water_temperature, coffee_amount, coffee_temperature],
            )[0]
            == "ok"
        )

    @command(default_output=format_output("Powering on"))
    def on(self) -> bool:
        """Power on."""
        return self.send("Machine_ON")[0] == "ok"

    @command(default_output=format_output("Powering off"))
    def off(self) -> bool:
        """Power off."""
        return self.send("Machine_OFF")[0] == "ok"

    @command()
    def buzzer_frequency(self):
        """Unknown."""
        raise NotImplementedError()
        return self.send("Buzzer_Frequency_Time")[0] == "ok"
