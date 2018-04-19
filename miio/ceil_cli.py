# -*- coding: UTF-8 -*-
import logging
import sys

import click

import miio  # noqa: E402
from miio.click_common import (ExceptionHandlerGroup, validate_ip,
                               validate_token, )

_LOGGER = logging.getLogger(__name__)
pass_dev = click.make_pass_decorator(miio.Ceil)


def validate_percentage(ctx, param, value):
    value = int(value)
    if value < 1 or value > 100:
        raise click.BadParameter('Should be a positive int between 1-100.')
    return value


def validate_seconds(ctx, param, value):
    value = int(value)
    if value < 0 or value > 21600:
        raise click.BadParameter('Should be a positive int between 1-21600.')
    return value


def validate_scene(ctx, param, value):
    value = int(value)
    if value < 1 or value > 4:
        raise click.BadParameter('Should be a positive int between 1-4.')
    return value


@click.group(invoke_without_command=True, cls=ExceptionHandlerGroup)
@click.option('--ip', envvar="DEVICE_IP", callback=validate_ip)
@click.option('--token', envvar="DEVICE_TOKEN", callback=validate_token)
@click.option('-d', '--debug', default=False, count=True)
@click.pass_context
def cli(ctx, ip: str, token: str, debug: int):
    """A tool to command Xiaomi Philips LED Ceiling Lamp."""

    if debug:
        logging.basicConfig(level=logging.DEBUG)
        _LOGGER.info("Debug mode active")
    else:
        logging.basicConfig(level=logging.INFO)

    # if we are scanning, we do not try to connect.
    if ctx.invoked_subcommand == "discover":
        return

    if ip is None or token is None:
        click.echo("You have to give ip and token!")
        sys.exit(-1)

    dev = miio.Ceil(ip, token, debug)
    _LOGGER.debug("Connecting to %s with token %s", ip, token)

    ctx.obj = dev

    if ctx.invoked_subcommand is None:
        ctx.invoke(status)


@cli.command()
def discover():
    """Search for plugs in the network."""
    miio.Ceil.discover()


@cli.command()
@pass_dev
def status(dev: miio.Ceil):
    """Returns the state information."""
    res = dev.status()
    if not res:
        return  # bail out

    click.echo(click.style("Power: %s" % res.power, bold=True))
    click.echo("Brightness: %s" % res.brightness)
    click.echo("Color temperature: %s" % res.color_temperature)
    click.echo("Scene: %s" % res.scene)
    click.echo("Smart Night Light: %s" % res.smart_night_light)
    click.echo("Auto CCT: %s" % res.automatic_color_temperature)
    click.echo("Countdown of the delayed turn off: %s seconds"
               % res.delay_off_countdown)


@cli.command()
@pass_dev
def on(dev: miio.Ceil):
    """Power on."""
    click.echo("Power on: %s" % dev.on())


@cli.command()
@pass_dev
def off(dev: miio.Ceil):
    """Power off."""
    click.echo("Power off: %s" % dev.off())


@cli.command()
@click.argument('level', callback=validate_percentage, required=True,)
@pass_dev
def set_brightness(dev: miio.Ceil, level):
    """Set brightness level."""
    click.echo("Brightness: %s" % dev.set_brightness(level))


@cli.command()
@click.argument('level', callback=validate_percentage, required=True,)
@pass_dev
def set_color_temperature(dev: miio.Ceil, level):
    """Set CCT level."""
    click.echo("Color temperature level: %s" %
               dev.set_color_temperature(level))


@cli.command()
@click.argument('seconds', callback=validate_seconds, required=True,)
@pass_dev
def delay_off(dev: miio.Ceil, seconds):
    """Set delay off in seconds."""
    click.echo("Delay off: %s" % dev.delay_off(seconds))


@cli.command()
@click.argument('scene', callback=validate_scene, required=True,)
@pass_dev
def set_scene(dev: miio.Ceil, scene):
    """Set scene number."""
    click.echo("Eyecare Scene: %s" % dev.set_scene(scene))


@cli.command()
@pass_dev
def smart_night_light_on(dev: miio.Ceil):
    """Smart Night Light on."""
    click.echo("Smart Night Light On: %s" % dev.smart_night_light_on())


@cli.command()
@pass_dev
def smart_night_light_off(dev: miio.Ceil):
    """Smart Night Light off."""
    click.echo("Smart Night Light Off: %s" % dev.smart_night_light_off())


@cli.command()
@pass_dev
def automatic_color_temperature_on(dev: miio.Ceil):
    """Auto CCT on."""
    click.echo("Auto CCT On: %s" % dev.automatic_color_temperature_on())


@cli.command()
@pass_dev
def automatic_color_temperature_off(dev: miio.Ceil):
    """Auto CCT on."""
    click.echo("Auto CCT Off: %s" % dev.automatic_color_temperature_off())


if __name__ == "__main__":
    cli()
