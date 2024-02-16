import logging
from pprint import pformat as pf

import click

from miio import Device

_LOGGER = logging.getLogger(__name__)


@click.command()
@click.option("--host", required=True, prompt=True)
@click.option("--token", required=True, prompt=True)
@click.argument("properties", type=str, nargs=-1, required=True)
def test_properties(host: str, token: str, properties):
    """Helper to test device properties."""
    dev = Device(host, token)

    def ok(x):
        click.echo(click.style(str(x), fg="green", bold=True))

    def fail(x):
        click.echo(click.style(str(x), fg="red", bold=True))

    try:
        model = dev.info().model
    except Exception as ex:
        _LOGGER.warning("Unable to obtain device model: %s", ex)
        model = "<unavailable>"

    click.echo(f"Testing properties {properties} for {model}")
    valid_properties = {}
    max_property_len = max(len(p) for p in properties)
    for property in properties:
        try:
            click.echo(f"Testing {property:{max_property_len + 2}} ", nl=False)
            value = dev.get_properties([property])
            # Handle list responses
            if isinstance(value, list):
                # unwrap single-element lists
                if len(value) == 1:
                    value = value.pop()
                # report on unexpected multi-element lists
                elif len(value) > 1:
                    _LOGGER.error("Got an array as response: %s", value)
                # otherwise we received an empty list, which we consider here as None
                else:
                    value = None

            if value is None:
                fail("None")
            else:
                valid_properties[property] = value
                ok(f"{repr(value)} {type(value)}")
        except Exception as ex:
            _LOGGER.warning("Unable to request %s: %s", property, ex)

    click.echo(
        f"Found {len(valid_properties)} valid properties, testing max_properties.."
    )

    props_to_test = list(valid_properties.keys())
    max_properties = -1
    while len(props_to_test) > 0:
        try:
            click.echo(
                f"Testing {len(props_to_test)} properties at once ({' '.join(props_to_test)}): ",
                nl=False,
            )
            resp = dev.get_properties(props_to_test)

            if len(resp) == len(props_to_test):
                max_properties = len(props_to_test)
                ok(f"OK for {max_properties} properties")
                break
            else:
                removed_property = props_to_test.pop()
                fail(
                    f"Got different amount of properties ({len(props_to_test)}) than requested ({len(resp)}), removing {removed_property}"
                )

        except Exception as ex:
            removed_property = props_to_test.pop()
            msg = f"Unable to request properties: {ex} - removing {removed_property} for next try"
            _LOGGER.warning(msg)
            fail(ex)

    non_empty_properties = {k: v for k, v in valid_properties.items() if v is not None}

    click.echo(click.style("\nPlease copy the results below to your report", bold=True))
    click.echo("### Results ###")
    click.echo(f"Model: {model}")
    _LOGGER.debug(f"All responsive properties:\n{pf(valid_properties)}")
    click.echo(f"Total responsives: {len(valid_properties)}")
    click.echo(f"Total non-empty: {len(non_empty_properties)}")
    click.echo(f"All non-empty properties:\n{pf(non_empty_properties)}")
    click.echo(f"Max properties: {max_properties}")

    return "Done"
