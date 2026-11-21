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
