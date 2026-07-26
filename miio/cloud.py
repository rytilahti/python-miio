import json
import logging
from typing import TYPE_CHECKING

import click
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

try:
    from rich import print as echo
except ImportError:
    echo = click.echo


from miio.exceptions import CloudException

_LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from micloud import MiCloud  # noqa: F401

LOGIN_CAPTCHA_HINT = (
    "Login failed. Xiaomi serves a captcha on password logins for many "
    "accounts, which micloud cannot answer. Try QR code login instead: "
    "'miiocli cloud --qr list', or CloudInterface(use_qr=True)."
)

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

    _raw_data: dict = PrivateAttr(default=None)

    @property
    def is_child(self):
        """Return True for gateway sub devices."""
        return self.parent_id != ""

    @property
    def raw_data(self):
        """Return the raw data."""
        return self._raw_data

    model_config = ConfigDict(extra="allow")


class CloudInterface:
    """Cloud interface for obtaining a list of devices and their tokens.

    The :meth:`get_devices` takes the locale string (e.g., 'us') as an argument,
    defaulting to all known locales (accessible through :meth:`available_locales`).

    Two login methods are available. Password login uses the ``micloud``
    library. QR code login is implemented locally and works when Xiaomi serves a
    captcha on password login, which it currently does for many accounts.

    Example::

        ci = CloudInterface(username="foo", password=...)
        devs = ci.get_devices()
        for did, dev in devs.items():
            print(dev)

    Or, without a password::

        ci = CloudInterface(use_qr=True)
        devs = ci.get_devices(locale="de")
    """

    def __init__(self, username=None, password=None, use_qr=False, on_qr=None):
        """Initialize the interface.

        :param username: account name, for password login.
        :param password: account password, for password login.
        :param use_qr: authenticate by QR code instead, needing no password.
        :param on_qr: called with ``(png_bytes, login_url)`` when using QR
            login. Defaults to writing the image to a temporary file.
        """
        if not use_qr and not (username and password):
            raise CloudException(
                "Either username and password, or use_qr=True, is required"
            )

        self.username = username
        self.password = password
        self.use_qr = use_qr
        self._on_qr = on_qr
        self._backend = None

    def _login(self):
        if self._backend is not None:
            _LOGGER.debug("Already logged in, skipping login")
            return

        self._backend = self._qr_backend() if self.use_qr else self._micloud_backend()

    def _qr_backend(self):
        from miio.cloud_qr import QrCodeLogin

        backend = QrCodeLogin(on_qr=self._on_qr)
        backend.login()
        return backend

    def _micloud_backend(self):
        try:
            from micloud import MiCloud  # noqa: F811
            from micloud.micloudexception import MiCloudAccessDenied
        except ImportError as ex:
            raise CloudException(
                "You need to install 'micloud' package to use cloud interface"
            ) from ex

        backend: MiCloud = MiCloud(username=self.username, password=self.password)
        try:  # login() can either return False or raise an exception on failure
            if not backend.login():
                raise CloudException(LOGIN_CAPTCHA_HINT)
        except MiCloudAccessDenied as ex:
            raise CloudException(LOGIN_CAPTCHA_HINT) from ex

        return backend

    def _parse_device_list(self, data, locale):
        """Parse device list response from micloud."""
        devs = {}
        for single_entry in data:
            single_entry["locale"] = locale
            devinfo = CloudDeviceInfo.model_validate(single_entry)
            devinfo._raw_data = single_entry
            devs[f"{devinfo.did}_{locale}"] = devinfo

        return devs

    @classmethod
    def available_locales(cls) -> dict[str, str]:
        """Return available locales.

        The value is the human-readable name of the locale.
        """
        return AVAILABLE_LOCALES

    def get_devices(self, locale: str | None = None) -> dict[str, CloudDeviceInfo]:
        """Return a list of available devices keyed with a device id.

        If no locale is given, all known locales are browsed. If a device id is already
        seen in another locale, it is excluded from the results.
        """
        _LOGGER.debug("Getting devices for locale %s", locale)
        self._login()
        if locale is not None and locale != "all":
            return self._parse_device_list(
                self._backend.get_devices(country=locale), locale=locale
            )

        all_devices: dict[str, CloudDeviceInfo] = {}
        for loc in AVAILABLE_LOCALES:
            if loc == "all":
                continue
            devs = self.get_devices(locale=loc)
            for did, dev in devs.items():
                all_devices[did] = dev
        return all_devices


@click.group(invoke_without_command=True)
@click.option("--username", default=None, help="Account name for password login.")
@click.option("--password", default=None, help="Account password.")
@click.option(
    "--qr",
    "use_qr",
    is_flag=True,
    default=False,
    help="Log in by scanning a QR code in the Xiaomi Home app, with no password. "
    "Use this if password login fails with a captcha.",
)
@click.pass_context
def cloud(ctx: click.Context, username, password, use_qr):
    """Cloud commands."""
    if use_qr:
        ctx.obj = CloudInterface(use_qr=True)
    else:
        try:
            import micloud  # noqa: F401
        except ImportError as ex:
            _LOGGER.error("micloud is not installed, no cloud access available")
            raise CloudException("install micloud for cloud access") from ex

        if not username:
            username = click.prompt("Username")
        if not password:
            password = click.prompt("Password", hide_input=True)
        ctx.obj = CloudInterface(username=username, password=password)

    if ctx.invoked_subcommand is None:
        ctx.invoke(cloud_list)


@cloud.command(name="list")
@click.pass_context
@click.option("--locale", prompt=True, type=click.Choice(AVAILABLE_LOCALES.keys()))
@click.option("--raw", is_flag=True, default=False)
def cloud_list(ctx: click.Context, locale: str | None, raw: bool):
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

        echo("\tOther fields:")
        for field, value in (dev.model_extra or {}).items():
            echo(f"\t\t{field}: {value}")

    if not devices:
        echo(f"Unable to find devices for locale {locale}")
