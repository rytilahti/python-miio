# -*- coding: UTF-8 -*-
import logging
import click
import ast
import sys
import ipaddress

if sys.version_info < (3, 4):
    print("To use this script you need python 3.4 or newer, got %s" %
          sys.version_info)
    sys.exit(1)

import mirobo  # noqa: E402

_LOGGER = logging.getLogger(__name__)
pass_dev = click.make_pass_decorator(mirobo.Plug)


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

    dev = mirobo.Plug(ip, token, debug)
    _LOGGER.debug("Connecting to %s with token %s", ip, token)

    ctx.obj = dev

    if ctx.invoked_subcommand is None:
        ctx.invoke(status)


@cli.command()
def discover():
    """Search for plugs in the network."""
    mirobo.Plug.discover()


@cli.command()
@pass_dev
def status(dev: mirobo.Plug):
    """Returns the state information."""
    res = dev.status()
    if not res:
        return  # bail out

    click.echo(click.style("Power: %s" % res.power, bold=True))
    click.echo("Temperature: %s %%" % res.temperature)
    click.echo("Current: %s %%" % res.current)


@cli.command()
@pass_dev
def on(dev: mirobo.Plug):
    """Power on."""
    click.echo("Power on: %s" % dev.on())


@cli.command()
@pass_dev
def off(dev: mirobo.Plug):
    """Power off."""
    click.echo("Power off: %s" % dev.off())


@cli.command()
@click.argument('cmd', required=True)
@click.argument('parameters', required=False)
@pass_dev
def raw_command(dev: mirobo.Plug, cmd, parameters):
    """Run a raw command."""
    params = []  # type: Any
    if parameters:
        params = ast.literal_eval(parameters)
    click.echo("Sending cmd %s with params %s" % (cmd, params))
    click.echo(dev.raw_command(cmd, params))


if __name__ == "__main__":
    cli()
