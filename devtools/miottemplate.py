import logging

import click

from containers import Device

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
    data = file.read()
    gen = Generator(data)
    print(gen.generate())


@cli.command()
@click.argument("type")
def download(type):
    """Download description file for model."""
    import requests

    url = f"https://miot-spec.org/miot-spec-v2/instance?type={type}"
    content = requests.get(url)
    save_to = f"{type}.json"
    click.echo(f"Saving data to {save_to}")
    with open(save_to, "w") as f:
        f.write(content.text)


if __name__ == "__main__":
    cli()
