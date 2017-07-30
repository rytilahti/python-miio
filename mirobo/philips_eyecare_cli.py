# -*- coding: UTF-8 -*-
import logging
import click
import sys
import ipaddress

if sys.version_info < (3, 4):
    print("To use this script you need python 3.4 or newer, got %s" %
          sys.version_info)
    sys.exit(1)

import mirobo  # noqa: E402

_LOGGER = logging.getLogger(__name__)
pass_dev = click.make_pass_decorator(mirobo.PhilipsEyecare)


def validate_bright(ctx, param, value):
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


def validate_ip(ctx, param, value):
    try:
        ipaddress.ip_address(value)
        return value
    except ValueError as ex:
        raise click.BadParameter("Invalid IP: %s" % ex)


def validate_token(ctx, param, value):
    token_len = len(value)
    if token_len != 32:
        raise click.BadParameter("Token length != 32 chars: %s" % token_len)
    return value


@click.group(invoke_without_command=True)
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

    dev = mirobo.PhilipsEyecare(ip, token, debug)
    _LOGGER.debug("Connecting to %s with token %s", ip, token)

    ctx.obj = dev

    if ctx.invoked_subcommand is None:
        ctx.invoke(status)


@cli.command()
def discover():
    """Search for plugs in the network."""
    mirobo.PhilipsEyecare.discover()


@cli.command()
@pass_dev
def status(dev: mirobo.PhilipsEyecare):
    """Returns the state information."""
    res = dev.status()
    if not res:
        return  # bail out

    click.echo(click.style("Power: %s" % res.power, bold=True))
    click.echo("Brightness: %s" % res.bright)
    click.echo("Eye Fatigue Reminder: %s" % res.notifystatus)
    click.echo("Ambient Light: %s" % res.ambstatus)
    click.echo("Ambient Light Brightness: %s" % res.ambvalue)
    click.echo("Eyecare Mode: %s" % res.eyecare)
    click.echo("Eyecare Scene: %s" % res.scene_num)
    click.echo("Night Light: %s " % res.bls)
    click.echo("Delay Off: %s minutes" % res.dvalue)


@cli.command()
@pass_dev
def on(dev: mirobo.PhilipsEyecare):
    """Power on."""
    click.echo("Power on: %s" % dev.on())


@cli.command()
@pass_dev
def off(dev: mirobo.PhilipsEyecare):
    """Power off."""
    click.echo("Power off: %s" % dev.off())


@cli.command()
@click.argument('level', callback=validate_bright, required=True,)
@pass_dev
def set_bright(dev: mirobo.PhilipsEyecare, level):
    """Set brightness level."""
    click.echo("Brightness: %s" % dev.set_bright(level))


@cli.command()
@click.argument('scene', callback=validate_scene, required=True,)
@pass_dev
def set_scene(dev: mirobo.PhilipsEyecare, scene):
    """Set eyecare scene number."""
    click.echo("Eyecare Scene: %s" % dev.set_user_scene(scene))


@cli.command()
@click.argument('minutes', callback=validate_minutes, required=True,)
@pass_dev
def delay_off(dev: mirobo.PhilipsEyecare, minutes):
    """Set delay off in minutes."""
    click.echo("Delay off: %s" % dev.delay_off(minutes))


@cli.command()
@pass_dev
def bl_on(dev: mirobo.PhilipsEyecare):
    """Night Light on."""
    click.echo("Night Light On: %s" % dev.bl_on())


@cli.command()
@pass_dev
def bl_off(dev: mirobo.PhilipsEyecare):
    """Night Light off."""
    click.echo("Night Light off: %s" % dev.bl_off())


@cli.command()
@pass_dev
def notify_on(dev: mirobo.PhilipsEyecare):
    """Eye Fatigue Reminder On."""
    click.echo("Eye Fatigue Reminder On: %s" % dev.notify_user_on())


@cli.command()
@pass_dev
def notify_off(dev: mirobo.PhilipsEyecare):
    """Eye Fatigue Reminder off."""
    click.echo("Eye Fatigue Reminder Off: %s" % dev.notify_user_off())


@cli.command()
@pass_dev
def ambient_on(dev: mirobo.PhilipsEyecare):
    """Ambient Light on."""
    click.echo("Ambient Light On: %s" % dev.amb_on())


@cli.command()
@pass_dev
def ambient_off(dev: mirobo.PhilipsEyecare):
    """Ambient Light off."""
    click.echo("Ambient Light Off: %s" % dev.amb_off())


@cli.command()
@click.argument('level', callback=validate_bright, required=True,)
@pass_dev
def set_amb_bright(dev: mirobo.PhilipsEyecare, level):
    """Set Ambient Light brightness level."""
    click.echo("Ambient Light Brightness: %s" % dev.set_amb_bright(level))


if __name__ == "__main__":
    cli()
