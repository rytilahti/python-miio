"""Click commons.

This file contains common functions for cli tools.
"""
import sys
if sys.version_info < (3, 5):
    print("To use this script you need python 3.5 or newer, got %s" %
          sys.version_info)
    sys.exit(1)
import click
import ipaddress
import miio
import logging


_LOGGER = logging.getLogger(__name__)


def validate_ip(ctx, param, value):
    if value is None:
        return None
    try:
        ipaddress.ip_address(value)
        return value
    except ValueError as ex:
        raise click.BadParameter("Invalid IP: %s" % ex)


def validate_token(ctx, param, value):
    if value is None:
        return None
    token_len = len(value)
    if token_len != 32:
        raise click.BadParameter("Token length != 32 chars: %s" % token_len)
    return value


class ExceptionHandlerGroup(click.Group):
    """Add a simple group for catching the miio-related exceptions.

    This simplifies catching the exceptions from different click commands.

    Idea from https://stackoverflow.com/a/44347763
    """
    def __call__(self, *args, **kwargs):
        try:
            return self.main(*args, **kwargs)
        except miio.DeviceException as ex:
            _LOGGER.debug("Exception: %s", ex, exc_info=True)
            click.echo(click.style("Error: %s" % ex, fg='red', bold=True))
