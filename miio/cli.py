# -*- coding: UTF-8 -*-
import logging
import click
from miio.click_common import (
    ExceptionHandlerGroup, DeviceGroupMeta, GlobalContextObject
)

_LOGGER = logging.getLogger(__name__)


@click.group(cls=ExceptionHandlerGroup)
@click.option('-d', '--debug', default=False, count=True)
@click.pass_context
def cli(ctx, debug: int):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
        _LOGGER.info("Debug mode active")
    else:
        logging.basicConfig(level=logging.INFO)

    ctx.obj = GlobalContextObject(
        debug=debug
    )


for device_class in DeviceGroupMeta.device_classes:
    cli.add_command(device_class.get_device_group())


def create_cli():
    return cli(auto_envvar_prefix="MIIO")


if __name__ == '__main__':
    create_cli()
