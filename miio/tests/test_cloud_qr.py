import base64
import json

import pytest

from miio.cloud import CloudInterface
from miio.cloud_qr import QrCodeLogin, _rc4, _strip_prefix
from miio.exceptions import CloudException

KEY = base64.b64encode(b"0123456789abcdef").decode()


def test_rc4_is_symmetric():
    data = b"the same call encrypts and decrypts"
    assert _rc4(base64.b64decode(KEY), _rc4(base64.b64decode(KEY), data)) == data


def _textbook_rc4(key: bytes, data: bytes) -> bytes:
    """Reference RC4 with no keystream discard, for comparison only."""
    s = list(range(256))
    j = 0
    for i in range(256):
        j = (j + s[i] + key[i % len(key)]) & 0xFF
        s[i], s[j] = s[j], s[i]
    out = bytearray()
    i = j = 0
    for byte in data:
        i = (i + 1) & 0xFF
        j = (j + s[i]) & 0xFF
        s[i], s[j] = s[j], s[i]
        out.append(byte ^ s[(s[i] + s[j]) & 0xFF])
    return bytes(out)


def test_rc4_discards_the_first_1024_keystream_bytes():
    """Xiaomi skips 1024 keystream bytes before the payload. Without that skip
    the ciphertext differs and the server rejects the request."""
    key = base64.b64decode(KEY)
    payload = b"abc"

    assert len(_rc4(key, payload)) == len(payload)
    assert _rc4(key, payload) != _textbook_rc4(key, payload)


def test_seal_unseal_round_trips():
    payload = json.dumps({"getVirtualModel": False, "getHuamiDevices": 0})
    assert QrCodeLogin._unseal(KEY, QrCodeLogin._seal(KEY, payload)).decode() == payload


def test_unseal_requires_the_base64_decode():
    """Feeding the raw response body to RC4 without base64-decoding it first
    yields bytes that are not valid UTF-8, so responses silently fail to
    parse."""
    sealed = QrCodeLogin._seal(KEY, '{"code": 0}')
    assert QrCodeLogin._unseal(KEY, sealed).decode() == '{"code": 0}'

    not_decoded = _rc4(base64.b64decode(KEY), sealed.encode())
    with pytest.raises((UnicodeDecodeError, ValueError)):
        json.loads(not_decoded)


def test_signed_nonce_is_deterministic():
    ssecurity = base64.b64encode(b"secret-secret-16").decode()
    nonce = base64.b64encode(b"nonce-12").decode()
    first = QrCodeLogin._signed_nonce(ssecurity, nonce)
    assert first == QrCodeLogin._signed_nonce(ssecurity, nonce)
    assert base64.b64decode(first)


def test_nonce_is_valid_base64_of_the_expected_length():
    raw = base64.b64decode(QrCodeLogin._nonce())
    assert len(raw) == 12  # 8 random bytes plus a 4-byte minute counter


@pytest.mark.parametrize(
    ("country", "expected"),
    [
        ("cn", "https://api.io.mi.com/app"),
        ("de", "https://de.api.io.mi.com/app"),
        ("us", "https://us.api.io.mi.com/app"),
    ],
)
def test_api_url_per_locale(country, expected):
    """Mainland China has no locale prefix, every other region does."""
    assert QrCodeLogin.api_url(country) == expected


def test_strip_prefix_handles_xiaomis_json_guard():
    assert _strip_prefix('&&&START&&&{"a": 1}') == {"a": 1}
    assert _strip_prefix('{"a": 1}') == {"a": 1}


def test_post_before_login_raises():
    with pytest.raises(CloudException):
        QrCodeLogin()._post("de", "/home/device_list", "{}")


def test_get_devices_tolerates_an_empty_response(mocker):
    backend = QrCodeLogin()
    mocker.patch.object(backend, "_post", return_value=None)
    assert backend.get_devices(country="de") == []


def test_get_devices_returns_the_device_list(mocker):
    backend = QrCodeLogin()
    mocker.patch.object(
        backend, "_post", return_value={"result": {"list": [{"did": "1", "name": "x"}]}}
    )
    assert backend.get_devices(country="de") == [{"did": "1", "name": "x"}]


# -- CloudInterface wiring ----------------------------------------------


def test_cloud_interface_requires_credentials_or_qr():
    with pytest.raises(CloudException):
        CloudInterface()
    with pytest.raises(CloudException):
        CloudInterface(username="foo")


def test_cloud_interface_accepts_qr_without_a_password():
    ci = CloudInterface(use_qr=True)
    assert ci.use_qr is True
    assert ci.password is None


def test_qr_login_is_used_when_requested(mocker):
    backend = mocker.Mock()
    login = mocker.patch("miio.cloud_qr.QrCodeLogin", return_value=backend)

    ci = CloudInterface(use_qr=True)
    ci._login()

    login.assert_called_once()
    backend.login.assert_called_once()
    assert ci._backend is backend


def test_login_happens_only_once(mocker):
    backend = mocker.Mock()
    mocker.patch("miio.cloud_qr.QrCodeLogin", return_value=backend)

    ci = CloudInterface(use_qr=True)
    ci._login()
    ci._login()

    backend.login.assert_called_once()


def test_devices_are_parsed_from_the_qr_backend(mocker):
    """The QR backend returns the same records as micloud, so the existing
    parsing must work unchanged."""
    record = {
        "localip": "192.168.1.2",
        "token": "0" * 32,
        "did": "123",
        "mac": "aa:bb:cc:dd:ee:ff",
        "name": "Robot",
        "model": "xiaomi.vacuum.b108gl",
        "desc": "Idle",
        "parent_id": "",
        "parent_model": "",
        "ssid": "wifi",
        "bssid": "aa:bb:cc:00:11:22",
        "isOnline": True,
        "rssi": -55,
    }
    backend = mocker.Mock()
    backend.get_devices.return_value = [record]
    mocker.patch("miio.cloud_qr.QrCodeLogin", return_value=backend)

    devices = CloudInterface(use_qr=True).get_devices(locale="de")

    assert len(devices) == 1
    info = devices["123_de"]
    assert info.did == "123"
    assert info.model == "xiaomi.vacuum.b108gl"
    assert info.ip == "192.168.1.2"
    assert info.is_online is True
    assert info.is_child is False
