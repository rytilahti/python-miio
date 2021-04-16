import logging

import click

from miio import Discovery
from miio.click_common import (
    DeviceGroupMeta,
    ExceptionHandlerGroup,
    GlobalContextObject,
    json_output,
)
from miio.miioprotocol import MiIOProtocol

_LOGGER = logging.getLogger(__name__)


@click.group(cls=ExceptionHandlerGroup)
@click.option("-d", "--debug", default=False, count=True)
@click.option(
    "-o",
    "--output",
    type=click.Choice(["default", "json", "json_pretty"]),
    default="default",
)
@click.version_option()
@click.pass_context
def cli(ctx, debug: int, output: str):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
        _LOGGER.info("Debug mode active")
    else:
        logging.basicConfig(level=logging.INFO)

    if output in ("json", "json_pretty"):
        output_func = json_output(pretty=output == "json_pretty")
    else:
        output_func = None

    ctx.obj = GlobalContextObject(debug=debug, output=output_func)


for device_class in DeviceGroupMeta.device_classes:
    cli.add_command(device_class.get_device_group())


@click.command()
@click.option("--mdns/--no-mdns", default=True, is_flag=True)
@click.option("--handshake/--no-handshake", default=True, is_flag=True)
@click.option("--network", default=None)
@click.option("--timeout", type=int, default=5)
def discover(mdns, handshake, network, timeout):
    """Discover devices using both handshake and mdns methods."""
    if handshake:
        MiIOProtocol.discover(addr=network, timeout=timeout)
    if mdns:
        Discovery.discover_mdns(timeout=timeout)


cli.add_command(discover)


def create_cli():
    return cli(auto_envvar_prefix="MIIO")


if __name__ == "__main__":
    create_cli()
