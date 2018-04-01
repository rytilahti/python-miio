# -*- coding: UTF-8 -*-
import logging
import sys

import click

import miio  # noqa: E402
from miio.click_common import (ExceptionHandlerGroup, validate_ip,
                               validate_token, )

_LOGGER = logging.getLogger(__name__)
pass_dev = click.make_pass_decorator(miio.PhilipsEyecare)


def validate_brightness(ctx, param, value):
    value = int(value)
    if value < 1 or value > 100:
        raise click.BadParameter('Should be a positive int between 1-100.')
    return value


def validate_minutes(ctx, param, value):
    value = int(value)
    if value < 0 or value > 60:
        raise click.BadParameter('Should be a positive int between 1-60.')
    return value


def validate_scene(ctx, param, value):
    value = int(value)
    if value < 1 or value > 3:
        raise click.BadParameter('Should be a positive int between 1-3.')
    return value


@click.group(invoke_without_command=True, cls=ExceptionHandlerGroup)
@click.option('--ip', envvar="DEVICE_IP", callback=validate_ip)
@click.option('--token', envvar="DEVICE_TOKEN", callback=validate_token)
@click.option('-d', '--debug', default=False, count=True)
@click.pass_context
def cli(ctx, ip: str, token: str, debug: int):
    """A tool to command Xiaomi Philips Eyecare Smart Lamp 2."""

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

    dev = miio.PhilipsEyecare(ip, token, debug)
    _LOGGER.debug("Connecting to %s with token %s", ip, token)

    ctx.obj = dev

    if ctx.invoked_subcommand is None:
        ctx.invoke(status)


@cli.command()
def discover():
    """Search for plugs in the network."""
    miio.PhilipsEyecare.discover()


@cli.command()
@pass_dev
def status(dev: miio.PhilipsEyecare):
    """Returns the state information."""
    res = dev.status()
    if not res:
        return  # bail out

    click.echo(click.style("Power: %s" % res.power, bold=True))
    click.echo("Brightness: %s" % res.brightness)
    click.echo("Eye Fatigue Reminder: %s" % res.reminder)
    click.echo("Ambient Light: %s" % res.ambient)
    click.echo("Ambient Light Brightness: %s" % res.ambient_brightness)
    click.echo("Eyecare Mode: %s" % res.eyecare)
    click.echo("Eyecare Scene: %s" % res.scene)
    click.echo("Night Light: %s " % res.smart_night_light)
    click.echo("Countdown of the delayed turn off: %s minutes"
               % res.delay_off_countdown)


@cli.command()
@pass_dev
def on(dev: miio.PhilipsEyecare):
    """Power on."""
    click.echo("Power on: %s" % dev.on())


@cli.command()
@pass_dev
def off(dev: miio.PhilipsEyecare):
    """Power off."""
    click.echo("Power off: %s" % dev.off())


@cli.command()
@click.argument('level', callback=validate_brightness, required=True,)
@pass_dev
def set_brightness(dev: miio.PhilipsEyecare, level):
    """Set brightness level."""
    click.echo("Brightness: %s" % dev.set_brightness(level))


@cli.command()
@click.argument('scene', callback=validate_scene, required=True,)
@pass_dev
def set_scene(dev: miio.PhilipsEyecare, scene):
    """Set eyecare scene number."""
    click.echo("Eyecare Scene: %s" % dev.set_scene(scene))


@cli.command()
@click.argument('minutes', callback=validate_minutes, required=True,)
@pass_dev
def delay_off(dev: miio.PhilipsEyecare, minutes):
    """Set delay off in minutes."""
    click.echo("Delay off: %s" % dev.delay_off(minutes))


@cli.command()
@pass_dev
def bl_on(dev: miio.PhilipsEyecare):
    """Night Light on."""
    click.echo("Night Light On: %s" % dev.smart_night_light_on())


@cli.command()
@pass_dev
def bl_off(dev: miio.PhilipsEyecare):
    """Night Light off."""
    click.echo("Night Light off: %s" % dev.smart_night_light_off())


@cli.command()
@pass_dev
def notify_on(dev: miio.PhilipsEyecare):
    """Eye Fatigue Reminder On."""
    click.echo("Eye Fatigue Reminder On: %s" % dev.reminder_on())


@cli.command()
@pass_dev
def notify_off(dev: miio.PhilipsEyecare):
    """Eye Fatigue Reminder off."""
    click.echo("Eye Fatigue Reminder Off: %s" % dev.reminder_off())


@cli.command()
@pass_dev
def ambient_on(dev: miio.PhilipsEyecare):
    """Ambient Light on."""
    click.echo("Ambient Light On: %s" % dev.ambient_on())


@cli.command()
@pass_dev
def ambient_off(dev: miio.PhilipsEyecare):
    """Ambient Light off."""
    click.echo("Ambient Light Off: %s" % dev.ambient_off())


@cli.command()
@click.argument('level', callback=validate_brightness, required=True,)
@pass_dev
def set_ambient_brightness(dev: miio.PhilipsEyecare, level):
    """Set Ambient Light brightness level."""
    click.echo("Ambient Light Brightness: %s" %
               dev.set_ambient_brightness(level))


if __name__ == "__main__":
    cli()
