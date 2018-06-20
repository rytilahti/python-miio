# -*- coding: UTF-8 -*-
import ast
import logging
import sys
from typing import Any  # noqa: F401

import click

import miio  # noqa: E402
from miio.click_common import (ExceptionHandlerGroup, validate_ip,
                               validate_token, )

_LOGGER = logging.getLogger(__name__)
pass_dev = click.make_pass_decorator(miio.ChuangmiPlug)


@click.group(invoke_without_command=True, cls=ExceptionHandlerGroup)
@click.option('--ip', envvar="DEVICE_IP", callback=validate_ip)
@click.option('--token', envvar="DEVICE_TOKEN", callback=validate_token)
@click.option('-d', '--debug', default=False, count=True)
@click.pass_context
def cli(ctx, ip: str, token: str, debug: int):
    """A tool to command Xiaomi Smart Plug."""
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

    dev = miio.ChuangmiPlug(ip, token, debug)
    _LOGGER.debug("Connecting to %s with token %s", ip, token)

    ctx.obj = dev

    if ctx.invoked_subcommand is None:
        ctx.invoke(status)


@cli.command()
def discover():
    """Search for plugs in the network."""
    miio.ChuangmiPlug.discover()


@cli.command()
@pass_dev
def status(dev: miio.ChuangmiPlug):
    """Returns the state information."""
    res = dev.status()
    if not res:
        return  # bail out

    click.echo(click.style("Power: %s" % res.power, bold=True))
    click.echo("Temperature: %s" % res.temperature)


@cli.command()
@pass_dev
def on(dev: miio.ChuangmiPlug):
    """Power on."""
    click.echo("Power on: %s" % dev.on())


@cli.command()
@pass_dev
def off(dev: miio.ChuangmiPlug):
    """Power off."""
    click.echo("Power off: %s" % dev.off())


@cli.command()
@click.argument('cmd', required=True)
@click.argument('parameters', required=False)
@pass_dev
def raw_command(dev: miio.ChuangmiPlug, cmd, parameters):
    """Run a raw command."""
    params = []  # type: Any
    if parameters:
        params = ast.literal_eval(parameters)
    click.echo("Sending cmd %s with params %s" % (cmd, params))
    click.echo(dev.raw_command(cmd, params))


if __name__ == "__main__":
    cli()
