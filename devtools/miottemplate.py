import logging
from pathlib import Path

import click
import requests
from containers import Device, ModelMapping

MIOTSPEC_MAPPING = Path("model_miotspec_mapping.json")

_LOGGER = logging.getLogger(__name__)


@click.group()
@click.option("-d", "--debug")
def cli(debug):
    lvl = logging.INFO
    if debug:
        lvl = logging.DEBUG

    logging.basicConfig(level=lvl)


class Generator:
    def __init__(self, data):
        self.data = data

    def print_infos(self):
        dev = Device.from_json(self.data)
        click.echo(
            f"Device '{dev.type}': {dev.description} with {len(dev.services)} services"
        )
        for serv in dev.services:
            click.echo(f"\n* Service {serv}")

            if serv.properties:
                click.echo("\n\t## Properties ##")
                for prop in serv.properties:
                    click.echo(f"\t\tsiid {serv.iid}: {prop}")
                    if prop.value_list:
                        for value in prop.value_list:
                            click.echo(f"\t\t\t{value}")
                    if prop.value_range:
                        click.echo(f"\t\t\tRange: {prop.value_range}")

            if serv.actions:
                click.echo("\n\t## Actions ##")
                for act in serv.actions:
                    click.echo(f"\t\tsiid {serv.iid}: {act}")

            if serv.events:
                click.echo("\n\t## Events ##")
                for evt in serv.events:
                    click.echo(f"\t\tsiid {serv.iid}: {evt}")

    def generate(self):
        dev = Device.from_json(self.data)

        for serv in dev.services:
            _LOGGER.info("Service: %s", serv)
            for prop in serv.properties:
                _LOGGER.info("  * Property %s", prop)

            for act in serv.actions:
                _LOGGER.info("  * Action %s", act)

            for ev in serv.events:
                _LOGGER.info("  * Event %s", ev)

        return dev.as_code()


@cli.command()
@click.argument("file", type=click.File())
def generate(file):
    """Generate pseudo-code python for given file."""
    raise NotImplementedError(
        "Disabled until miot support gets improved, please use print command instead"
    )
    data = file.read()
    gen = Generator(data)
    click.echo(gen.generate())


@cli.command(name="print")
@click.argument("file", type=click.File())
def _print(file):
    """Print out device information (props, actions, events)."""
    data = file.read()
    gen = Generator(data)

    gen.print_infos()


@cli.command()
def download_mapping():
    """Download model<->urn mapping."""
    click.echo(
        "Downloading and saving model<->urn mapping to %s" % MIOTSPEC_MAPPING.name
    )
    url = "http://miot-spec.org/miot-spec-v2/instances?status=all"
    res = requests.get(url)

    with MIOTSPEC_MAPPING.open("w") as f:
        f.write(res.text)


def get_mapping() -> ModelMapping:
    with MIOTSPEC_MAPPING.open("r") as f:
        return ModelMapping.from_json(f.read())


@cli.command()
def list():
    """List all entries in the model<->urn mapping file."""
    mapping = get_mapping()

    for inst in mapping.instances:
        click.echo(f"* {repr(inst)}")


@cli.command()
@click.option("--urn", default=None)
@click.argument("model", required=False)
@click.pass_context
def download(ctx, urn, model):
    """Download description file for model."""

    if urn is None:
        if model is None:
            click.echo("You need to specify either the model or --urn")
            return

        if not MIOTSPEC_MAPPING.exists():
            click.echo(
                "miotspec mapping doesn't exist, downloading to %s"
                % MIOTSPEC_MAPPING.name
            )
            ctx.invoke(download_mapping)

        mapping = get_mapping()
        urn = mapping.urn_for_model(model)

    url = f"https://miot-spec.org/miot-spec-v2/instance?type={urn}"
    content = requests.get(url)
    save_to = f"{urn}.json"
    click.echo(f"Saving data to {save_to}")
    with open(save_to, "w") as f:
        f.write(content.text)


if __name__ == "__main__":
    cli()
