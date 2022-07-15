import logging
from pprint import pprint
from typing import TYPE_CHECKING, Dict, List, Optional

import attr
import click

_LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from micloud import MiCloud  # noqa: F401

AVAILABLE_LOCALES = ["cn", "de", "i2", "ru", "sg", "us"]


class CloudException(Exception):
    """Exception raised for cloud connectivity issues."""


@attr.s(auto_attribs=True)
class CloudDeviceInfo:
    """Container for device data from the cloud.

    Note that only some selected information is directly exposed, but you can access the
    raw data using `raw_data`.
    """

    did: str
    token: str
    name: str
    model: str
    ip: str
    description: str
    parent_id: str
    ssid: str
    mac: str
    locale: List[str]
    raw_data: str = attr.ib(repr=False)

    @classmethod
    def from_micloud(cls, response, locale):
        micloud_to_info = {
            "did": "did",
            "token": "token",
            "name": "name",
            "model": "model",
            "ip": "localip",
            "description": "desc",
            "ssid": "ssid",
            "parent_id": "parent_id",
            "mac": "mac",
        }
        data = {k: response[v] for k, v in micloud_to_info.items()}
        return cls(raw_data=response, locale=[locale], **data)


class CloudInterface:
    """Cloud interface using micloud library.

    Currently used only for obtaining the list of registered devices.

    Example::

        ci = CloudInterface(username="foo", password=...)
        devs = ci.get_devices()
        for did, dev in devs.items():
            print(dev)
    """

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self._micloud = None

    def _login(self):
        if self._micloud is not None:
            _LOGGER.debug("Already logged in, skipping login")
            return

        try:
            from micloud import MiCloud  # noqa: F811
            from micloud.micloudexception import MiCloudAccessDenied
        except ImportError:
            raise CloudException(
                "You need to install 'micloud' package to use cloud interface"
            )

        self._micloud = MiCloud = MiCloud(
            username=self.username, password=self.password
        )

        try:  # login() can either return False or raise an exception on failure
            if not self._micloud.login():
                raise CloudException("Login failed")
        except MiCloudAccessDenied as ex:
            raise CloudException("Login failed") from ex

    def _parse_device_list(self, data, locale):
        """Parse device list response from micloud."""
        devs = {}
        for single_entry in data:
            devinfo = CloudDeviceInfo.from_micloud(single_entry, locale)
            devs[devinfo.did] = devinfo

        return devs

    def get_devices(self, locale: Optional[str] = None) -> Dict[str, CloudDeviceInfo]:
        """Return a list of available devices keyed with a device id.

        If no locale is given, all known locales are browsed. If a device id is already
        seen in another locale, it is excluded from the results.
        """
        self._login()
        if locale is not None:
            return self._parse_device_list(
                self._micloud.get_devices(country=locale), locale=locale
            )

        all_devices: Dict[str, CloudDeviceInfo] = {}
        for loc in AVAILABLE_LOCALES:
            devs = self.get_devices(locale=loc)
            for did, dev in devs.items():
                if did in all_devices:
                    _LOGGER.debug("Already seen device with %s, appending", did)
                    all_devices[did].locale.extend(dev.locale)
                    continue
                all_devices[did] = dev
        return all_devices


@click.group(invoke_without_command=True)
@click.option("--username", prompt=True)
@click.option("--password", prompt=True)
@click.pass_context
def cloud(ctx: click.Context, username, password):
    """Cloud commands."""
    try:
        import micloud  # noqa: F401
    except ImportError:
        _LOGGER.error("micloud is not installed, no cloud access available")
        raise CloudException("install micloud for cloud access")

    ctx.obj = CloudInterface(username=username, password=password)
    if ctx.invoked_subcommand is None:
        ctx.invoke(cloud_list)


@cloud.command(name="list")
@click.pass_context
@click.option("--locale", prompt=True, type=click.Choice(AVAILABLE_LOCALES + ["all"]))
@click.option("--raw", is_flag=True, default=False)
def cloud_list(ctx: click.Context, locale: Optional[str], raw: bool):
    """List devices connected to the cloud account."""

    ci = ctx.obj
    if locale == "all":
        locale = None

    devices = ci.get_devices(locale=locale)

    if raw:
        click.echo(f"Printing devices for {locale}")
        click.echo("===================================")
        for dev in devices.values():
            pprint(dev.raw_data)  # noqa: T203
        click.echo("===================================")

    for dev in devices.values():
        if dev.parent_id:
            continue  # we handle children separately

        click.echo(f"== {dev.name} ({dev.description}) ==")
        click.echo(f"\tModel: {dev.model}")
        click.echo(f"\tToken: {dev.token}")
        click.echo(f"\tIP: {dev.ip} (mac: {dev.mac})")
        click.echo(f"\tDID: {dev.did}")
        click.echo(f"\tLocale: {', '.join(dev.locale)}")
        childs = [x for x in devices.values() if x.parent_id == dev.did]
        if childs:
            click.echo("\tSub devices:")
            for c in childs:
                click.echo(f"\t\t{c.name}")
                click.echo(f"\t\t\tDID: {c.did}")
                click.echo(f"\t\t\tModel: {c.model}")

    if not devices:
        click.echo(f"Unable to find devices for locale {locale}")
