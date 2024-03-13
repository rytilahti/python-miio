import json
import logging
from typing import TYPE_CHECKING, Dict, Optional

import click

try:
    from pydantic.v1 import BaseModel, Field
except ImportError:
    from pydantic import BaseModel, Field

try:
    from rich import print as echo
except ImportError:
    echo = click.echo


from miio.exceptions import CloudException

_LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from micloud import MiCloud  # noqa: F401

AVAILABLE_LOCALES = {
    "all": "All",
    "cn": "China",
    "de": "Germany",
    "i2": "i2",  # unknown
    "ru": "Russia",
    "sg": "Singapore",
    "us": "USA",
}


class CloudDeviceInfo(BaseModel):
    """Model for the xiaomi cloud device information.

    Note that only some selected information is directly exposed, raw data is available
    using :meth:`raw_data`.
    """

    ip: str = Field(alias="localip")
    token: str
    did: str
    mac: str
    name: str
    model: str
    description: str = Field(alias="desc")

    locale: str

    parent_id: str
    parent_model: str

    # network info
    ssid: str
    bssid: str
    is_online: bool = Field(alias="isOnline")
    rssi: int

    _raw_data: dict = Field(repr=False)

    @property
    def is_child(self):
        """Return True for gateway sub devices."""
        return self.parent_id != ""

    @property
    def raw_data(self):
        """Return the raw data."""
        return self._raw_data

    class Config:
        extra = "allow"


class CloudInterface:
    """Cloud interface using micloud library.

    You can use this to obtain a list of devices and their tokens.
    The :meth:`get_devices` takes the locale string (e.g., 'us') as an argument,
    defaulting to all known locales (accessible through :meth:`available_locales`).

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

        self._micloud: MiCloud = MiCloud(username=self.username, password=self.password)
        try:  # login() can either return False or raise an exception on failure
            if not self._micloud.login():
                raise CloudException("Login failed")
        except MiCloudAccessDenied as ex:
            raise CloudException("Login failed") from ex

    def _parse_device_list(self, data, locale):
        """Parse device list response from micloud."""
        devs = {}
        for single_entry in data:
            single_entry["locale"] = locale
            devinfo = CloudDeviceInfo.parse_obj(single_entry)
            devinfo._raw_data = single_entry
            devs[f"{devinfo.did}_{locale}"] = devinfo

        return devs

    @classmethod
    def available_locales(cls) -> Dict[str, str]:
        """Return available locales.

        The value is the human-readable name of the locale.
        """
        return AVAILABLE_LOCALES

    def get_devices(self, locale: Optional[str] = None) -> Dict[str, CloudDeviceInfo]:
        """Return a list of available devices keyed with a device id.

        If no locale is given, all known locales are browsed. If a device id is already
        seen in another locale, it is excluded from the results.
        """
        _LOGGER.debug("Getting devices for locale %s", locale)
        self._login()
        if locale is not None and locale != "all":
            return self._parse_device_list(
                self._micloud.get_devices(country=locale), locale=locale
            )

        all_devices: Dict[str, CloudDeviceInfo] = {}
        for loc in AVAILABLE_LOCALES:
            if loc == "all":
                continue
            devs = self.get_devices(locale=loc)
            for did, dev in devs.items():
                all_devices[did] = dev
        return all_devices


@click.group(invoke_without_command=True)
@click.option("--username", prompt=True)
@click.option("--password", prompt=True, hide_input=True)
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
@click.option("--locale", prompt=True, type=click.Choice(AVAILABLE_LOCALES.keys()))
@click.option("--raw", is_flag=True, default=False)
def cloud_list(ctx: click.Context, locale: Optional[str], raw: bool):
    """List devices connected to the cloud account."""

    ci = ctx.obj

    devices = ci.get_devices(locale=locale)

    if raw:
        jsonified = json.dumps([dev.raw_data for dev in devices.values()], indent=4)
        print(jsonified)  # noqa: T201
        return

    for dev in devices.values():
        if dev.parent_id:
            continue  # we handle children separately

        echo(f"== {dev.name} ({dev.description}) ==")
        echo(f"\tModel: {dev.model}")
        echo(f"\tToken: {dev.token}")
        echo(f"\tIP: {dev.ip} (mac: {dev.mac})")
        echo(f"\tDID: {dev.did}")
        echo(f"\tLocale: {dev.locale}")
        childs = [x for x in devices.values() if x.parent_id == dev.did]
        if childs:
            echo("\tSub devices:")
            for c in childs:
                echo(f"\t\t{c.name}")
                echo(f"\t\t\tDID: {c.did}")
                echo(f"\t\t\tModel: {c.model}")

        other_fields = dev.__fields_set__ - set(dev.__fields__.keys())
        echo("\tOther fields:")
        for field in other_fields:
            if field.startswith("_"):
                continue

            echo(f"\t\t{field}: {getattr(dev, field)}")

    if not devices:
        echo(f"Unable to find devices for locale {locale}")
