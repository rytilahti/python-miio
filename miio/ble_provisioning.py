"""Wi-Fi provisioning of Xiaomi "combo" (Wi-Fi + BLE) devices over Bluetooth LE.

Newer Xiaomi Wi-Fi devices built on combo modules (e.g. Bouffalo BL602, advertised as
``MIBLE_*``) no longer open a ``*_miap*`` access point after a Wi-Fi reset, so
:meth:`miio.Device.configure_wifi` cannot reach them.  The vendor app provisions them over
BLE instead: a Xiaomi "standard auth" key exchange (ECDH P-256) followed by an encrypted
Wi-Fi configuration package.  This module implements that flow.

The BLE transport needs the optional ``bleak`` dependency (``python-miio[ble]``); the
protocol helpers work without it.

Observations on ``xiaomi.derh.lite`` (BL602, BLE firmware 3.6.5_0581):

* the account ``uid`` is mandatory: without it the device accepts the configuration and
  reports success, but never joins the network (a random ``bind_key`` does not help);
* a non-existent ``country_domain`` (e.g. ``zz``) is accepted, the device joins Wi-Fi but
  cannot reach the cloud;
* the miIO token is not delivered over BLE and stays hidden in the handshake, so local
  control needs the token from the cloud (``miiocli cloud list``) after provisioning with a
  real region; blocking the device's internet access afterwards keeps the token valid.
"""

from __future__ import annotations

import asyncio
import logging
import struct
import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import IntEnum
from typing import Any

import click
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers.aead import AESCCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from .exceptions import DeviceException

_LOGGER = logging.getLogger(__name__)


def _char_uuid(short: int) -> str:
    return f"0000{short:04x}-0000-1000-8000-00805f9b34fb"


MI_SERVICE_UUID = _char_uuid(0xFE95)
CHAR_STATUS = _char_uuid(0x0005)
CHAR_CONTROL = _char_uuid(0x0010)
CHAR_DATA = _char_uuid(0x0019)

ACK_READY = bytes.fromhex("00000101")
ACK_SUCCESS = bytes.fromhex("00000100")
SINGLE_ACK = bytes.fromhex("00000300")
OP_DEV_INFO_GET = bytes.fromhex("a2000000")
OP_REG_START_WO_PKI = bytes.fromhex("15000000")
OP_REG_SUCCESS = bytes.fromhex("11000000")

PKG_DEV_INFO = 0x00
PKG_PUBKEY = 0x03
PKG_WIFI_CONFIG = 0x0F

#: payload bytes per data frame (frame = 2-byte sequence number + payload, ATT MTU 23)
DMTU = 18


class BleProvisioningException(DeviceException):
    """Raised when BLE provisioning fails."""


class ProvisioningStatus(IntEnum):
    """Status byte notified by the device on characteristic 0x0005."""

    Waiting = 0
    Connecting = 1
    RouterConnected = 2
    CloudConnected = 3
    BleError = 4
    RouterError = 5
    DhcpError = 16
    AuthError = 17
    NetworkNotFound = 18
    ServerError = 19


FAILURE_STATES = {
    ProvisioningStatus.BleError,
    ProvisioningStatus.RouterError,
    ProvisioningStatus.DhcpError,
    ProvisioningStatus.AuthError,
    ProvisioningStatus.NetworkNotFound,
    ProvisioningStatus.ServerError,
}


class WifiConfigField(IntEnum):
    """TLV types of the Wi-Fi configuration package."""

    Uid = 0
    Ssid = 1
    Password = 2
    GmtOffset = 5
    CountryDomain = 6
    TimeZone = 7
    ConfigType = 8
    BindKey = 9
    CountryCode = 10


@dataclass
class MiBeacon:
    """Parsed Xiaomi BLE advertisement (service data of UUID 0xFE95)."""

    frame_control: int
    product_id: int
    frame_counter: int
    mac: str | None = None
    capability: int | None = None

    @property
    def registered(self) -> bool:
        return bool(self.frame_control & 0x100)

    @property
    def auth_mode(self) -> int:
        """0 legacy, 1 secure auth, 2 standard auth."""
        return (self.frame_control >> 10) & 3

    @property
    def bond_ability(self) -> int | None:
        """3 means combo (Wi-Fi + BLE)."""
        return None if self.capability is None else (self.capability >> 3) & 3

    @property
    def awaiting_combo_setup(self) -> bool:
        return self.bond_ability == 3 and not self.registered and self.auth_mode == 2


def parse_mibeacon(data: bytes) -> MiBeacon | None:
    """Parse MiBeacon service data, return None if it is too short."""
    if len(data) < 5:
        return None
    frame_control, product_id, counter = struct.unpack("<HHB", data[:5])
    beacon = MiBeacon(frame_control, product_id, counter)
    pos = 5
    if frame_control & 0x10 and len(data) >= pos + 6:
        beacon.mac = ":".join(f"{b:02X}" for b in reversed(data[pos : pos + 6]))
        pos += 6
    if frame_control & 0x20 and len(data) > pos:
        beacon.capability = data[pos]
    return beacon


def split_frames(data: bytes, dmtu: int = DMTU) -> list[bytes]:
    """Split a payload into data frames: 1-based u16 sequence number + payload."""
    return [
        struct.pack("<H", i // dmtu + 1) + data[i : i + dmtu]
        for i in range(0, len(data), dmtu)
    ]


def transfer_start(pkg_type: int, frame_count: int) -> bytes:
    """Control packet announcing a multi-frame transfer."""
    return bytes([0, 0, 0, pkg_type]) + struct.pack("<H", frame_count)


@dataclass
class ComboKeys:
    dev_key: bytes
    app_key: bytes
    dev_iv: bytes
    app_iv: bytes


def derive_combo_keys(shared_secret: bytes) -> ComboKeys:
    """HKDF-SHA256 over the ECDH secret as used by combo devices."""
    k = HKDF(hashes.SHA256(), 64, None, b"mible-setup-info").derive(shared_secret)
    return ComboKeys(
        dev_key=k[0:16], app_key=k[16:32], dev_iv=k[32:36], app_iv=k[36:40]
    )


@dataclass
class WifiConfig:
    """Wi-Fi settings sent to the device.

    :param uid: Xiaomi account id the device binds itself to (required by tested firmware).
    :param country_domain: cloud region (``us``, ``de``, ``sg``, ``cn``, ...).
    """

    ssid: str
    password: str
    uid: int | None
    country_domain: str
    tz: str = "UTC"
    gmt_offset: int = 0
    country_code: str | None = None
    bind_key: str | None = None
    config_type: str = "app"

    def to_tlv(self) -> bytes:
        def tlv(field: WifiConfigField, value: bytes) -> bytes:
            if len(value) > 255:
                raise ValueError(f"{field.name} is too long")
            return bytes([field, len(value)]) + value

        domain = self.country_domain.lower()
        domain_bytes = (
            b"\0\0\0" if domain == "cn" else domain.encode()[:3].ljust(3, b"\0")
        )
        out = b""
        if self.uid is not None:
            out += tlv(WifiConfigField.Uid, struct.pack("<q", self.uid))
        out += tlv(WifiConfigField.Ssid, self.ssid.encode())
        out += tlv(WifiConfigField.Password, self.password.encode())
        out += tlv(WifiConfigField.GmtOffset, struct.pack("<i", self.gmt_offset))
        out += tlv(WifiConfigField.CountryDomain, domain_bytes)
        out += tlv(WifiConfigField.TimeZone, self.tz.encode())
        out += tlv(WifiConfigField.ConfigType, self.config_type.encode())
        if self.country_code:
            out += tlv(WifiConfigField.CountryCode, self.country_code.upper().encode())
        if self.bind_key:
            out += tlv(WifiConfigField.BindKey, self.bind_key.encode())
        return out


def encrypt_wifi_config(keys: ComboKeys, plaintext: bytes, counter: int = 1) -> bytes:
    """Counter (u16) followed by AES-128-CCM ciphertext with a 4-byte tag."""
    nonce = keys.app_iv + bytes(4) + struct.pack("<I", counter)
    sealed = AESCCM(keys.app_key, tag_length=4).encrypt(nonce, plaintext, None)
    return struct.pack("<H", counter) + sealed


class _Channel:
    """Framing on the data characteristic, plus control and status notifications."""

    def __init__(self, client: Any, timeout: float = 10.0) -> None:
        self._client = client
        self._timeout = timeout
        self.data: asyncio.Queue[bytes] = asyncio.Queue()
        self.control: asyncio.Queue[bytes] = asyncio.Queue()
        self.status: list[int] = []
        self.on_status: Callable[[int], None] | None = None

    async def start(self) -> None:
        await self._client.start_notify(CHAR_STATUS, self._status_received)
        await self._client.start_notify(CHAR_CONTROL, self._control_received)
        await self._client.start_notify(CHAR_DATA, self._data_received)

    def _status_received(self, _: Any, payload: bytearray) -> None:
        if payload:
            if (not self.status or self.status[-1] != payload[0]) and self.on_status:
                self.on_status(payload[0])
            self.status.append(payload[0])

    def _control_received(self, _: Any, payload: bytearray) -> None:
        self.control.put_nowait(bytes(payload))

    def _data_received(self, _: Any, payload: bytearray) -> None:
        self.data.put_nowait(bytes(payload))

    async def write_control(self, payload: bytes) -> None:
        await self._client.write_gatt_char(CHAR_CONTROL, payload, response=False)

    async def _write_data(self, payload: bytes) -> None:
        await self._client.write_gatt_char(CHAR_DATA, payload, response=False)

    async def _next(self) -> bytes:
        try:
            return await asyncio.wait_for(self.data.get(), self._timeout)
        except TimeoutError as ex:
            raise BleProvisioningException("timeout waiting for the device") from ex

    async def receive(self) -> tuple[int, bytes]:
        packet = await self._next()
        if packet[:3] == b"\0\0\x02":
            await self._write_data(SINGLE_ACK)
            return packet[3], packet[4:]
        if packet[:3] != b"\0\0\0" or len(packet) < 6:
            raise BleProvisioningException(f"unexpected packet {packet.hex()}")
        pkg_type, count = packet[3], struct.unpack("<H", packet[4:6])[0]
        await self._write_data(ACK_READY)
        parts: dict[int, bytes] = {}
        while len(parts) < count:
            frame = await self._next()
            seq = struct.unpack("<H", frame[:2])[0]
            if seq:
                parts[seq] = frame[2:]
        await self._write_data(ACK_SUCCESS)
        return pkg_type, b"".join(parts[i] for i in range(1, count + 1))

    async def send(self, pkg_type: int, payload: bytes) -> None:
        frames = split_frames(payload)
        await self._write_data(transfer_start(pkg_type, len(frames)))
        ack = await self._next()
        if ack != ACK_READY:
            raise BleProvisioningException(f"device not ready: {ack.hex()}")
        for frame in frames:
            await self._write_data(frame)
        while True:
            ack = await self._next()
            if ack == ACK_SUCCESS:
                return
            if ack[:4] == bytes.fromhex("00000105"):  # resend the listed frames
                for i in range(4, len(ack) - 1, 2):
                    await self._write_data(
                        frames[struct.unpack("<H", ack[i : i + 2])[0] - 1]
                    )
                continue
            raise BleProvisioningException(f"package {pkg_type} rejected: {ack.hex()}")


@dataclass
class ProvisioningResult:
    did: str
    status: ProvisioningStatus | None


async def provision_client(
    client: Any,
    config: WifiConfig,
    *,
    wait: float = 60.0,
    on_status: Callable[[int], None] | None = None,
) -> ProvisioningResult:
    """Run the provisioning flow on a connected bleak-compatible client."""
    channel = _Channel(client)
    channel.on_status = on_status
    await channel.start()

    await channel.write_control(OP_DEV_INFO_GET)
    _, info = await channel.receive()
    did = info[4:].rstrip(b"\0").decode(errors="replace")
    _LOGGER.debug("Device id: %s", did)

    await channel.write_control(OP_REG_START_WO_PKI)
    private_key = ec.generate_private_key(ec.SECP256R1())
    public = private_key.public_key().public_bytes(
        Encoding.X962, PublicFormat.UncompressedPoint
    )
    await channel.send(PKG_PUBKEY, public[1:])
    pkg_type, device_public = await channel.receive()
    if pkg_type != PKG_PUBKEY or len(device_public) != 64:
        raise BleProvisioningException("unexpected key from the device")
    shared = private_key.exchange(
        ec.ECDH(),
        ec.EllipticCurvePublicKey.from_encoded_point(
            ec.SECP256R1(), b"\x04" + device_public
        ),
    )
    keys = derive_combo_keys(shared)

    await channel.send(PKG_WIFI_CONFIG, encrypt_wifi_config(keys, config.to_tlv()))
    _LOGGER.debug("Wi-Fi configuration accepted by the device")

    deadline = time.monotonic() + wait
    while time.monotonic() < deadline:
        await asyncio.sleep(0.5)
        if not channel.status:
            continue
        last = channel.status[-1]
        if last in FAILURE_STATES:
            raise BleProvisioningException(
                f"device reported {ProvisioningStatus(last).name}"
            )
        if last == ProvisioningStatus.CloudConnected:
            break
    status = None
    if channel.status and channel.status[-1] in ProvisioningStatus._value2member_map_:
        status = ProvisioningStatus(channel.status[-1])
    return ProvisioningResult(did=did, status=status)


async def scan(timeout: float = 12.0) -> dict[str, tuple[str | None, int, MiBeacon]]:
    """Collect MiBeacon advertisements, keyed by bleak address."""
    from bleak import BleakScanner

    found: dict[str, tuple[str | None, int, MiBeacon]] = {}

    def detected(device: Any, adv: Any) -> None:
        data = (adv.service_data or {}).get(MI_SERVICE_UUID)
        beacon = parse_mibeacon(bytes(data)) if data else None
        if beacon:
            found[device.address] = (adv.local_name or device.name, adv.rssi, beacon)

    async with BleakScanner(detection_callback=detected):
        await asyncio.sleep(timeout)
    return found


async def provision(
    address: str,
    config: WifiConfig,
    *,
    wait: float = 60.0,
    on_status: Callable[[int], None] | None = None,
) -> ProvisioningResult:
    """Connect to the device at the given bleak address and provision it."""
    from bleak import BleakClient

    async with BleakClient(address, timeout=25) as client:
        return await provision_client(client, config, wait=wait, on_status=on_status)


def _local_tz() -> str:
    try:
        import os

        path = os.path.realpath("/etc/localtime")
    except OSError:
        return "UTC"
    return path.split("zoneinfo/", 1)[1] if "zoneinfo/" in path else "UTC"


@click.group()
def ble() -> None:
    """Provision Xiaomi combo devices over Bluetooth (needs python-miio[ble])."""


@ble.command(name="scan")
@click.option("--timeout", type=float, default=12.0, show_default=True)
@click.option(
    "--all", "show_all", is_flag=True, help="Also list already set up devices."
)
def ble_scan(timeout: float, show_all: bool) -> None:
    """List devices waiting for BLE setup."""
    found = asyncio.run(scan(timeout))
    for address, (name, rssi, beacon) in found.items():
        if show_all or beacon.awaiting_combo_setup:
            click.echo(
                f"{address}  {name or '-'}  mac={beacon.mac}  product_id={beacon.product_id}"
                f"  rssi={rssi}  setup={'yes' if beacon.awaiting_combo_setup else 'no'}"
            )


@ble.command(name="provision")
@click.option("--address", help="bleak address; found by scanning if omitted.")
@click.option("--mac", help="BLE MAC to pick when several devices are in setup mode.")
@click.option("--ssid", required=True, help="2.4 GHz network name.")
@click.option("--password", prompt=True, hide_input=True)
@click.option("--uid", type=int, required=True, help="Your Xiaomi account id.")
@click.option("--region", required=True, help="Cloud region: cn, de, us, ru, sg, i2...")
@click.option("--tz", default=_local_tz, show_default="system", help="IANA time zone.")
@click.option("--gmt-offset", type=int, default=lambda: time.localtime().tm_gmtoff)
@click.option("--country", help="Wi-Fi country code, e.g. US.")
@click.option("--wait", type=float, default=60.0, show_default=True)
def ble_provision(
    address: str | None,
    mac: str | None,
    ssid: str,
    password: str,
    uid: int,
    region: str,
    tz: str,
    gmt_offset: int,
    country: str | None,
    wait: float,
) -> None:
    """Send Wi-Fi settings to a combo device in setup mode."""
    if address is None:
        found = asyncio.run(scan())
        candidates = [
            addr
            for addr, (_, _, beacon) in found.items()
            if beacon.awaiting_combo_setup
            and (mac is None or (beacon.mac or "").lower() == mac.lower())
        ]
        if len(candidates) != 1:
            raise click.ClickException(
                f"{len(candidates)} devices in setup mode found, use --address or --mac"
            )
        address = candidates[0]
    config = WifiConfig(
        ssid=ssid,
        password=password,
        uid=uid,
        country_domain=region,
        tz=tz,
        gmt_offset=gmt_offset,
        country_code=country,
    )

    def show(status: int) -> None:
        name = (
            ProvisioningStatus(status).name
            if status in ProvisioningStatus._value2member_map_
            else str(status)
        )
        click.echo(f"Device status: {name}")

    result = asyncio.run(provision(address, config, wait=wait, on_status=show))
    click.echo(
        f"Device {result.did}: {result.status.name if result.status else 'unknown'}"
    )
    click.echo("Fetch its token with 'miiocli cloud list' to control it locally.")
