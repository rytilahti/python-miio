import logging
from typing import Any, Dict

import click

from miio import Discovery
from miio.click_common import (
    DeviceGroupMeta,
    ExceptionHandlerGroup,
    GlobalContextObject,
    json_output,
)
from miio.miioprotocol import MiIOProtocol

from .cloud import cloud
from .devicefactory import factory
from .devtools import devtools

_LOGGER = logging.getLogger(__name__)


@click.group(cls=ExceptionHandlerGroup)
@click.option("-d", "--debug", default=False, count=True)
@click.option(
    "-o",
    "--output",
    type=click.Choice(["default", "json", "json_pretty"]),
    default="default",
)
@click.version_option(package_name="python-miio")
@click.pass_context
def cli(ctx, debug: int, output: str):
    logging_config: Dict[str, Any] = {
        "level": logging.DEBUG if debug > 0 else logging.INFO
    }
    try:
        from rich.logging import RichHandler

        rich_config = {
            "show_time": False,
        }
        logging_config["handlers"] = [RichHandler(**rich_config)]
        logging_config["format"] = "%(message)s"
    except ImportError:
        pass

    # The configuration should be converted to use dictConfig, but this keeps mypy happy for now
    logging.basicConfig(**logging_config)  # type: ignore

    if output in ("json", "json_pretty"):
        output_func = json_output(pretty=output == "json_pretty")
    else:
        output_func = None

    ctx.obj = GlobalContextObject(debug=debug, output=output_func)


for device_class in DeviceGroupMeta._device_classes:
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
cli.add_command(cloud)
cli.add_command(devtools)
cli.add_command(factory)


def create_cli():
    return cli(auto_envvar_prefix="MIIO")


if __name__ == "__main__":
    create_cli()
