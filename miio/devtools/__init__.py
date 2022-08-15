"""Command-line interface for devtools."""
import logging

import click

from .pcapparser import parse_pcap
from .propertytester import test_properties

_LOGGER = logging.getLogger(__name__)


@click.group(invoke_without_command=False)
@click.pass_context
def devtools(ctx: click.Context):
    """Tools for developers and troubleshooting."""


devtools.add_command(parse_pcap)
devtools.add_command(test_properties)
