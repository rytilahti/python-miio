import struct

import pytest
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers.aead import AESCCM
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from miio.ble_provisioning import (
    ACK_READY,
    ACK_SUCCESS,
    CHAR_CONTROL,
    CHAR_DATA,
    CHAR_STATUS,
    MI_SERVICE_UUID,
    OP_DEV_INFO_GET,
    OP_REG_SUCCESS,
    PKG_DEV_INFO,
    PKG_PUBKEY,
    PKG_WIFI_CONFIG,
    BleProvisioningException,
    ProvisioningStatus,
    WifiConfig,
    WifiConfigField,
    derive_combo_keys,
    encrypt_wifi_config,
    parse_mibeacon,
    provision_client,
    split_frames,
    transfer_start,
)


def parse_tlv(data: bytes) -> dict[int, bytes]:
    fields, i = {}, 0
    while i < len(data):
        fields[data[i]] = data[i + 2 : i + 2 + data[i + 1]]
        i += 2 + data[i + 1]
    return fields


def decrypt(keys, message: bytes) -> bytes:
    """Decrypt the way the device does."""
    counter = struct.unpack("<H", message[:2])[0]
    nonce = keys.app_iv + bytes(4) + struct.pack("<HH", counter, 0)
    return AESCCM(keys.app_key, tag_length=4).decrypt(nonce, message[2:], None)


def raw_public(key) -> bytes:
    return key.public_key().public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)[
        1:
    ]


class FakeDevice:
    """Device side of the combo flow, enough to drive provision_client()."""

    def __init__(self, final_status=ProvisioningStatus.CloudConnected):
        self.callbacks = {}
        self.private_key = ec.generate_private_key(ec.SECP256R1())
        self.keys = None
        self.config = None
        self.final_status = final_status
        self._incoming = None
        self._outgoing = None

    async def start_notify(self, uuid, callback):
        self.callbacks[uuid] = callback

    def notify(self, uuid, payload):
        self.callbacks[uuid](None, bytearray(payload))

    def start_sending(self, pkg_type, payload):
        self._outgoing = split_frames(payload)
        self.notify(CHAR_DATA, transfer_start(pkg_type, len(self._outgoing)))

    async def write_gatt_char(self, uuid, data, response=False):
        data = bytes(data)
        if uuid == CHAR_CONTROL:
            if data == OP_DEV_INFO_GET:
                self.start_sending(PKG_DEV_INFO, b"\x01\x00\x00\x00123456789")
            return
        if data[:3] == b"\0\0\0":
            self._incoming = (data[3], struct.unpack("<H", data[4:6])[0], {})
            self.notify(CHAR_DATA, ACK_READY)
        elif data == ACK_READY:
            for frame in self._outgoing:
                self.notify(CHAR_DATA, frame)
        elif data == ACK_SUCCESS:
            self._outgoing = None
        else:
            pkg_type, count, parts = self._incoming
            parts[struct.unpack("<H", data[:2])[0]] = data[2:]
            if len(parts) == count:
                self._incoming = None
                self.notify(CHAR_DATA, ACK_SUCCESS)
                self.handle(pkg_type, b"".join(parts[i] for i in range(1, count + 1)))

    def handle(self, pkg_type, payload):
        if pkg_type == PKG_PUBKEY:
            app_key = ec.EllipticCurvePublicKey.from_encoded_point(
                ec.SECP256R1(), b"\x04" + payload
            )
            self.keys = derive_combo_keys(self.private_key.exchange(ec.ECDH(), app_key))
            self.start_sending(PKG_PUBKEY, raw_public(self.private_key))
        elif pkg_type == PKG_WIFI_CONFIG:
            self.config = parse_tlv(decrypt(self.keys, payload))
            self.notify(CHAR_CONTROL, OP_REG_SUCCESS)
            self.notify(CHAR_STATUS, bytes([ProvisioningStatus.Connecting]))
            self.notify(CHAR_STATUS, bytes([self.final_status]))


def test_parse_mibeacon_combo_setup():
    beacon = parse_mibeacon(bytes.fromhex("3058ea4300665544332211" + "1d" + "2211"))
    assert beacon.product_id == 0x43EA
    assert beacon.mac == "11:22:33:44:55:66"
    assert beacon.auth_mode == 2
    assert beacon.bond_ability == 3
    assert not beacon.registered
    assert beacon.awaiting_combo_setup


def test_parse_mibeacon_too_short():
    assert parse_mibeacon(b"\x30\x58") is None


def test_split_frames():
    frames = split_frames(bytes(range(40)))
    assert [f[:2] for f in frames] == [b"\x01\x00", b"\x02\x00", b"\x03\x00"]
    assert b"".join(f[2:] for f in frames) == bytes(range(40))
    assert transfer_start(PKG_PUBKEY, 4) == bytes.fromhex("000000030400")


def test_wifi_config_roundtrip():
    keys = derive_combo_keys(bytes(range(32)))
    config = WifiConfig(
        ssid="Net",
        password="secret",
        uid=1234567890,
        country_domain="us",
        tz="Europe/Madrid",
        gmt_offset=3600,
        country_code="es",
    )
    fields = parse_tlv(decrypt(keys, encrypt_wifi_config(keys, config.to_tlv())))
    assert struct.unpack("<q", fields[WifiConfigField.Uid])[0] == 1234567890
    assert fields[WifiConfigField.Ssid] == b"Net"
    assert fields[WifiConfigField.Password] == b"secret"
    assert fields[WifiConfigField.CountryDomain] == b"us\0"
    assert fields[WifiConfigField.TimeZone] == b"Europe/Madrid"
    assert fields[WifiConfigField.CountryCode] == b"ES"
    assert struct.unpack("<i", fields[WifiConfigField.GmtOffset])[0] == 3600


def test_wifi_config_china_domain_is_empty():
    config = WifiConfig(ssid="a", password="b", uid=1, country_domain="cn")
    assert parse_tlv(config.to_tlv())[WifiConfigField.CountryDomain] == b"\0\0\0"


@pytest.mark.asyncio
async def test_provision_flow():
    device = FakeDevice()
    config = WifiConfig(ssid="Net", password="secret", uid=42, country_domain="us")
    seen = []
    result = await provision_client(device, config, wait=5, on_status=seen.append)
    assert result.did == "123456789"
    assert result.status == ProvisioningStatus.CloudConnected
    assert device.config[WifiConfigField.Ssid] == b"Net"
    assert struct.unpack("<q", device.config[WifiConfigField.Uid])[0] == 42
    assert seen == [ProvisioningStatus.Connecting, ProvisioningStatus.CloudConnected]


@pytest.mark.asyncio
async def test_provision_reports_router_error():
    device = FakeDevice(final_status=ProvisioningStatus.RouterError)
    config = WifiConfig(ssid="Net", password="wrong", uid=42, country_domain="us")
    with pytest.raises(BleProvisioningException):
        await provision_client(device, config, wait=5)


class ScriptedClient:
    """Bare client: records what the app writes, the test pushes device packets."""

    def __init__(self):
        self.callbacks = {}
        self.written = []

    async def start_notify(self, uuid, callback):
        self.callbacks[uuid] = callback

    async def write_gatt_char(self, uuid, data, response=False):
        self.written.append((uuid, bytes(data)))
        if self.on_write:
            self.on_write(uuid, bytes(data))

    on_write = None

    def push(self, uuid, payload):
        self.callbacks[uuid](None, bytearray(payload))


async def started_channel(timeout=1.0):
    from miio.ble_provisioning import _Channel

    client = ScriptedClient()
    channel = _Channel(client, timeout=timeout)
    await channel.start()
    return client, channel


def test_parse_mibeacon_without_mac_and_capability():
    beacon = parse_mibeacon(bytes.fromhex("0058ea4300"))
    assert beacon.mac is None
    assert beacon.capability is None
    assert beacon.bond_ability is None
    assert not beacon.awaiting_combo_setup


def test_wifi_config_optional_fields():
    plain = WifiConfig(ssid="a", password="b", uid=None, country_domain="us")
    assert WifiConfigField.Uid not in parse_tlv(plain.to_tlv())
    with_key = WifiConfig(
        ssid="a", password="b", uid=1, country_domain="us", bind_key="xyz"
    )
    assert parse_tlv(with_key.to_tlv())[WifiConfigField.BindKey] == b"xyz"
    with pytest.raises(ValueError):
        WifiConfig(ssid="x" * 300, password="b", uid=1, country_domain="us").to_tlv()


@pytest.mark.asyncio
async def test_channel_single_packet_and_control_frames():
    client, channel = await started_channel()
    client.push(CHAR_DATA, bytes.fromhex("00000200") + b"payload")
    assert await channel.receive() == (0, b"payload")
    assert client.written[-1] == (CHAR_DATA, bytes.fromhex("00000300"))

    client.push(CHAR_DATA, transfer_start(PKG_PUBKEY, 2))
    client.push(
        CHAR_DATA, bytes.fromhex("0000ffff")
    )  # control packet in between, ignored
    for frame in split_frames(bytes(range(20))):
        client.push(CHAR_DATA, frame)
    assert await channel.receive() == (PKG_PUBKEY, bytes(range(20)))


@pytest.mark.asyncio
async def test_channel_errors():
    client, channel = await started_channel(timeout=0.05)
    with pytest.raises(BleProvisioningException):
        await channel.receive()  # nothing arrives
    client.push(CHAR_DATA, b"\x05\x00junk")
    with pytest.raises(BleProvisioningException):
        await channel.receive()

    client.on_write = lambda uuid, data: (
        data[:3] == b"\0\0\0" and client.push(CHAR_DATA, bytes.fromhex("00000104"))
    )
    with pytest.raises(BleProvisioningException):
        await channel.send(PKG_PUBKEY, bytes(40))  # device not ready


@pytest.mark.asyncio
async def test_channel_resends_requested_frames():
    client, channel = await started_channel()
    answers = [ACK_READY, bytes.fromhex("000001050200"), ACK_SUCCESS]

    def on_write(uuid, data):
        if data[:3] == b"\0\0\0":
            client.push(CHAR_DATA, answers.pop(0))
        elif (
            data[:2] == b"\x03\x00"
        ):  # after the last frame: ask for frame 2, then accept
            client.push(CHAR_DATA, answers.pop(0))
        elif data[:2] == b"\x02\x00" and not answers[1:]:
            client.push(CHAR_DATA, answers.pop(0))

    client.on_write = on_write
    await channel.send(PKG_PUBKEY, bytes(40))
    sent = [data[:2] for _, data in client.written]
    assert sent.count(b"\x02\x00") == 2

    client.on_write = lambda uuid, data: (
        data[:3] == b"\0\0\0"
        and client.push(CHAR_DATA, ACK_READY)
        or (data[:2] == b"\x01\x00" and client.push(CHAR_DATA, b"\x00\x00\x01\x04"))
    )
    with pytest.raises(BleProvisioningException):
        await channel.send(PKG_PUBKEY, bytes(10))  # transfer rejected


@pytest.mark.asyncio
async def test_status_notifications():
    client, channel = await started_channel()
    seen = []
    channel.on_status = seen.append
    for payload in (b"", b"\x01", b"\x01", b"\x03"):
        client.push(CHAR_STATUS, payload)
    assert seen == [1, 3]
    assert channel.status == [1, 1, 3]


@pytest.mark.asyncio
async def test_provision_rejects_bad_device_key():
    device = FakeDevice()

    def bad_key(pkg_type, payload):
        if pkg_type == PKG_PUBKEY:
            device.start_sending(PKG_DEV_INFO, bytes(64))
        else:
            FakeDevice.handle(device, pkg_type, payload)

    device.handle = bad_key
    config = WifiConfig(ssid="Net", password="secret", uid=42, country_domain="us")
    with pytest.raises(BleProvisioningException):
        await provision_client(device, config, wait=1)


@pytest.mark.asyncio
async def test_provision_without_final_status():
    device = FakeDevice(final_status=7)  # unknown code: no failure, no cloud
    config = WifiConfig(ssid="Net", password="secret", uid=42, country_domain="zz")
    result = await provision_client(device, config, wait=0.6)
    assert result.status is None


class FakeBleak:
    """Stand-in for the bleak module."""

    def __init__(self, device):
        outer = self

        class Scanner:
            def __init__(self, detection_callback):
                self.callback = detection_callback

            async def __aenter__(self):
                found = type("D", (), {"address": "ADDR", "name": "MIBLE_BL602"})()
                adv = type(
                    "A",
                    (),
                    {
                        "service_data": {
                            MI_SERVICE_UUID: bytes.fromhex(
                                "3058ea4300665544332211" + "1d"
                            )
                        },
                        "local_name": None,
                        "rssi": -50,
                    },
                )()
                self.callback(found, adv)
                self.callback(found, type("A", (), {"service_data": {}})())
                return self

            async def __aexit__(self, *exc):
                return False

        class Client:
            def __init__(self, address, timeout):
                outer.connected_to = address

            async def __aenter__(self):
                return device

            async def __aexit__(self, *exc):
                return False

        self.BleakScanner = Scanner
        self.BleakClient = Client


@pytest.fixture
def fake_bleak(monkeypatch):
    import sys

    fake = FakeBleak(FakeDevice())
    monkeypatch.setitem(sys.modules, "bleak", fake)
    return fake


@pytest.mark.asyncio
async def test_scan_and_provision_with_bleak(fake_bleak):
    from miio.ble_provisioning import provision, scan

    found = await scan(timeout=0)
    assert list(found) == ["ADDR"]
    assert found["ADDR"][2].awaiting_combo_setup
    config = WifiConfig(ssid="Net", password="secret", uid=42, country_domain="us")
    result = await provision("ADDR", config, wait=5)
    assert fake_bleak.connected_to == "ADDR"
    assert result.status == ProvisioningStatus.CloudConnected


def test_local_tz(monkeypatch):
    import os

    from miio.ble_provisioning import _local_tz

    monkeypatch.setattr(os.path, "realpath", lambda p: "/usr/share/zoneinfo/Asia/Tokyo")
    assert _local_tz() == "Asia/Tokyo"
    monkeypatch.setattr(os.path, "realpath", lambda p: "/etc/localtime")
    assert _local_tz() == "UTC"

    def broken(path):
        raise OSError

    monkeypatch.setattr(os.path, "realpath", broken)
    assert _local_tz() == "UTC"


def test_cli(monkeypatch):
    from click.testing import CliRunner

    import miio.ble_provisioning as bp

    beacon = parse_mibeacon(bytes.fromhex("3058ea4300665544332211" + "1d"))
    other = parse_mibeacon(bytes.fromhex("3059ea4300665544332211" + "1d"))

    async def fake_scan(timeout=12.0):
        return {"A": ("MIBLE_BL602", -50, beacon), "B": (None, -70, other)}

    async def fake_provision(address, config, *, wait=60.0, on_status=None):
        on_status(ProvisioningStatus.Connecting)
        on_status(99)
        return bp.ProvisioningResult(
            did="123", status=ProvisioningStatus.CloudConnected
        )

    monkeypatch.setattr(bp, "scan", fake_scan)
    monkeypatch.setattr(bp, "provision", fake_provision)
    runner = CliRunner()

    out = runner.invoke(bp.ble, ["scan"]).output
    assert "A  MIBLE_BL602" in out
    assert "B " not in out
    assert "B  -" in runner.invoke(bp.ble, ["scan", "--all"]).output

    args = [
        "provision",
        "--ssid",
        "Net",
        "--password",
        "pw",
        "--uid",
        "1",
        "--region",
        "us",
    ]
    res = runner.invoke(bp.ble, args)
    assert res.exit_code == 0, res.output
    assert "Device status: Connecting" in res.output
    assert "Device status: 99" in res.output
    assert "Device 123: CloudConnected" in res.output

    res = runner.invoke(bp.ble, [*args, "--mac", "00:00:00:00:00:00"])
    assert res.exit_code != 0
    assert "0 devices in setup mode" in res.output

    async def nothing(address, config, *, wait=60.0, on_status=None):
        return bp.ProvisioningResult(did="5", status=None)

    monkeypatch.setattr(bp, "provision", nothing)
    res = runner.invoke(bp.ble, [*args, "--address", "X"])
    assert "Device 5: unknown" in res.output


@pytest.mark.asyncio
async def test_provision_device_reports_no_status():
    device = FakeDevice()

    def silent(pkg_type, payload):
        if pkg_type == PKG_WIFI_CONFIG:
            device.config = parse_tlv(decrypt(device.keys, payload))
        else:
            FakeDevice.handle(device, pkg_type, payload)

    device.handle = silent
    config = WifiConfig(ssid="Net", password="secret", uid=42, country_domain="us")
    result = await provision_client(device, config, wait=0.6)
    assert result.status is None
    assert device.config[WifiConfigField.Ssid] == b"Net"
