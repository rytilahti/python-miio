import base64
import json

import pytest
import requests

from miio.cloud import CloudInterface
from miio.cloud_qr import (
    QrCodeLogin,
    _rc4,
    _strip_prefix,
    print_qr_to_terminal,
)
from miio.exceptions import CloudException

KEY = base64.b64encode(b"0123456789abcdef").decode()
SSECURITY = base64.b64encode(b"secret-secret-16").decode()
NONCE = base64.b64encode(b"nonce-1234!!").decode()

QR_PAYLOAD = {
    "qr": "https://example.invalid/qr.png",
    "loginUrl": "https://example.invalid/login",
    "lp": "https://example.invalid/poll",
    "timeout": 5,
}
SESSION_PAYLOAD = {
    "userId": "42",
    "ssecurity": SSECURITY,
    "location": "https://example.invalid/sts",
}


class FakeResponse:
    """Minimal stand-in for a requests response."""

    def __init__(self, status_code=200, text="", content=b"", cookies=None):
        self.status_code = status_code
        self.text = text
        self.content = content
        self.cookies = cookies or {}


def logged_in(backend: QrCodeLogin) -> QrCodeLogin:
    backend.user_id = "42"
    backend._ssecurity = SSECURITY
    backend._service_token = "service-token"
    return backend


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


# -- QR presentation -----------------------------------------------------


def test_print_qr_to_terminal_writes_the_image_and_prints_both_routes(
    tmp_path, monkeypatch, capsys
):
    monkeypatch.setattr("tempfile.gettempdir", lambda: str(tmp_path))

    print_qr_to_terminal(b"\x89PNG-ish", "https://example.invalid/login")

    written = tmp_path / "miio-cloud-login-qr.png"
    assert written.read_bytes() == b"\x89PNG-ish"

    out = capsys.readouterr().out
    assert str(written) in out
    assert "https://example.invalid/login" in out


# -- login ---------------------------------------------------------------


def _login_session(mocker, backend, poll=None, sts_cookies=None):
    """Route the four GETs login() makes to canned responses."""
    poll = poll if poll is not None else FakeResponse(200, json.dumps(SESSION_PAYLOAD))
    # `or` would be wrong here: an empty dict is the "no token" case under test.
    if sts_cookies is None:
        sts_cookies = {"serviceToken": "service-token"}
    sts = FakeResponse(200, cookies=sts_cookies)

    def dispatch(url, **kwargs):
        if "longPolling/loginUrl" in url:
            return FakeResponse(200, "&&&START&&&" + json.dumps(QR_PAYLOAD))
        if url == QR_PAYLOAD["qr"]:
            return FakeResponse(200, content=b"png-bytes")
        if url == QR_PAYLOAD["lp"]:
            return poll
        return sts

    return mocker.patch.object(backend._session, "get", side_effect=dispatch)


def test_login_walks_the_whole_flow(mocker):
    seen = {}
    backend = QrCodeLogin(on_qr=lambda png, url: seen.update(png=png, url=url))
    _login_session(mocker, backend)

    assert backend.login() is True

    assert seen["png"] == b"png-bytes"
    assert seen["url"] == QR_PAYLOAD["loginUrl"]
    assert backend.user_id == "42"
    assert backend._service_token == "service-token"


def test_login_raises_when_xiaomi_returns_no_qr(mocker):
    backend = QrCodeLogin()
    mocker.patch.object(
        backend._session, "get", return_value=FakeResponse(200, json.dumps({}))
    )
    with pytest.raises(CloudException, match="did not return a login QR"):
        backend.login()


def test_login_raises_when_the_request_fails(mocker):
    backend = QrCodeLogin()
    mocker.patch.object(
        backend._session, "get", side_effect=requests.ConnectionError("no route")
    )
    with pytest.raises(CloudException, match="Unable to request a login QR"):
        backend.login()


def test_login_raises_when_the_code_is_never_scanned(mocker):
    """The long poll returns non-200 until the code expires."""
    backend = QrCodeLogin(on_qr=lambda *_: None, scan_timeout=0)
    _login_session(mocker, backend, poll=FakeResponse(401))
    with pytest.raises(CloudException, match="expired"):
        backend.login()


def test_login_raises_when_no_service_token_comes_back(mocker):
    backend = QrCodeLogin(on_qr=lambda *_: None)
    _login_session(mocker, backend, sts_cookies={})
    with pytest.raises(CloudException, match="No service token"):
        backend.login()


def test_long_poll_keeps_waiting_through_timeouts(mocker):
    """Xiaomi's long poll cycles; a timeout is normal and must not abort."""
    backend = QrCodeLogin()
    responses = [
        requests.Timeout("cycle"),
        FakeResponse(200, json.dumps(SESSION_PAYLOAD)),
    ]
    mocker.patch.object(
        backend._session,
        "get",
        side_effect=lambda *a, **k: (
            (_ for _ in ()).throw(r)
            if isinstance(r := responses.pop(0), Exception)
            else r
        ),
    )
    assert backend._long_poll("https://example.invalid/poll", timeout=5) == (
        SESSION_PAYLOAD
    )


def test_long_poll_surfaces_a_connection_error(mocker):
    backend = QrCodeLogin()
    mocker.patch.object(
        backend._session, "get", side_effect=requests.ConnectionError("down")
    )
    with pytest.raises(CloudException, match="Login polling failed"):
        backend._long_poll("https://example.invalid/poll", timeout=5)


# -- signed requests -----------------------------------------------------


def test_post_signs_the_request_and_decrypts_the_reply(mocker):
    backend = logged_in(QrCodeLogin())
    mocker.patch.object(QrCodeLogin, "_nonce", staticmethod(lambda: NONCE))
    signed = QrCodeLogin._signed_nonce(SSECURITY, NONCE)

    body = json.dumps({"code": 0, "result": {"list": []}})
    post = mocker.patch.object(
        backend._session,
        "post",
        return_value=FakeResponse(200, QrCodeLogin._seal(signed, body)),
    )

    assert backend._post("de", "/home/device_list", "{}") == json.loads(body)

    kwargs = post.call_args.kwargs
    assert kwargs["params"]["_nonce"] == NONCE
    assert kwargs["params"]["ssecurity"] == SSECURITY
    assert "signature" in kwargs["params"]
    assert "rc4_hash__" in kwargs["params"]
    # The payload must be encrypted, not sent in the clear.
    assert kwargs["params"]["data"] != "{}"
    assert kwargs["cookies"]["serviceToken"] == "service-token"
    assert kwargs["headers"]["MIOT-ENCRYPT-ALGORITHM"] == "ENCRYPT-RC4"
    assert post.call_args.args[0] == "https://de.api.io.mi.com/app/home/device_list"


def test_post_returns_none_on_a_non_200(mocker):
    backend = logged_in(QrCodeLogin())
    mocker.patch.object(backend._session, "post", return_value=FakeResponse(500))
    assert backend._post("de", "/home/device_list", "{}") is None


def test_post_returns_none_when_the_reply_will_not_decode(mocker):
    """A wrong key yields bytes that are not JSON; that must not raise."""
    backend = logged_in(QrCodeLogin())
    mocker.patch.object(
        backend._session, "post", return_value=FakeResponse(200, "not-base64-!!")
    )
    assert backend._post("de", "/home/device_list", "{}") is None


def test_post_surfaces_a_connection_error(mocker):
    backend = logged_in(QrCodeLogin())
    mocker.patch.object(
        backend._session, "post", side_effect=requests.ConnectionError("down")
    )
    with pytest.raises(CloudException, match="Cloud request failed"):
        backend._post("de", "/home/device_list", "{}")


def test_get_devices_reads_the_same_endpoint_as_micloud(mocker):
    backend = logged_in(QrCodeLogin())
    post = mocker.patch.object(backend, "_post", return_value={"result": {"list": []}})

    backend.get_devices(country="us")

    path = post.call_args.args[1]
    assert path == "/home/device_list"


def test_service_token_fetch_surfaces_a_connection_error(mocker):
    backend = QrCodeLogin()
    mocker.patch.object(
        backend._session, "get", side_effect=requests.ConnectionError("down")
    )
    with pytest.raises(CloudException, match="Unable to fetch the service token"):
        backend._service_token_for("https://example.invalid/sts")


# -- password login path -------------------------------------------------


def test_password_login_failure_points_at_qr(mocker):
    """The captcha is the usual cause now, so the error must say what to do."""
    from micloud.micloudexception import MiCloudAccessDenied

    micloud = mocker.Mock()
    micloud.login.side_effect = MiCloudAccessDenied("Access denied")
    mocker.patch("micloud.MiCloud", return_value=micloud)

    ci = CloudInterface(username="foo", password="bar")
    with pytest.raises(CloudException, match="--qr"):
        ci._login()


def test_password_login_failure_without_an_exception_also_points_at_qr(mocker):
    """micloud.login() can return False instead of raising."""
    micloud = mocker.Mock()
    micloud.login.return_value = False
    mocker.patch("micloud.MiCloud", return_value=micloud)

    ci = CloudInterface(username="foo", password="bar")
    with pytest.raises(CloudException, match="--qr"):
        ci._login()


def test_password_login_still_works(mocker):
    """QR is additive; the existing path must be untouched."""
    micloud = mocker.Mock()
    micloud.login.return_value = True
    factory = mocker.patch("micloud.MiCloud", return_value=micloud)

    ci = CloudInterface(username="foo", password="bar")
    ci._login()

    factory.assert_called_once_with(username="foo", password="bar")
    assert ci._backend is micloud


# -- CLI -----------------------------------------------------------------


def test_cli_qr_flag_skips_the_credential_prompts(mocker):
    """--qr must not ask for a username or password it will never use."""
    from click.testing import CliRunner

    from miio.cloud import cloud

    ci = mocker.Mock()
    ci.get_devices.return_value = {}
    factory = mocker.patch("miio.cloud.CloudInterface", return_value=ci)

    result = CliRunner().invoke(cloud, ["--qr", "list", "--locale", "de"], input="")

    assert result.exit_code == 0, result.output
    factory.assert_called_once_with(use_qr=True)
    assert "Username" not in result.output
    assert "Password" not in result.output


def test_cli_password_path_prompts_when_not_given(mocker):
    from click.testing import CliRunner

    from miio.cloud import cloud

    ci = mocker.Mock()
    ci.get_devices.return_value = {}
    factory = mocker.patch("miio.cloud.CloudInterface", return_value=ci)

    result = CliRunner().invoke(cloud, ["list", "--locale", "de"], input="user\npass\n")

    assert result.exit_code == 0, result.output
    factory.assert_called_once_with(username="user", password="pass")


def test_cli_accepts_credentials_as_options(mocker):
    from click.testing import CliRunner

    from miio.cloud import cloud

    ci = mocker.Mock()
    ci.get_devices.return_value = {}
    factory = mocker.patch("miio.cloud.CloudInterface", return_value=ci)

    result = CliRunner().invoke(
        cloud, ["--username", "u", "--password", "p", "list", "--locale", "de"]
    )

    assert result.exit_code == 0, result.output
    factory.assert_called_once_with(username="u", password="p")


def test_password_login_without_micloud_installed_explains_why(mocker):
    mocker.patch.dict("sys.modules", {"micloud": None})
    ci = CloudInterface(username="foo", password="bar")
    with pytest.raises(CloudException, match="micloud"):
        ci._login()


def test_cli_without_micloud_installed_explains_why(mocker):
    from click.testing import CliRunner

    from miio.cloud import cloud

    mocker.patch.dict("sys.modules", {"micloud": None})
    result = CliRunner().invoke(cloud, ["list", "--locale", "de"], input="u\np\n")

    assert result.exit_code != 0
    assert isinstance(result.exception, CloudException)


def test_cli_defaults_to_listing_when_no_subcommand_is_given(mocker):
    """`miiocli cloud --qr` with no subcommand should still list."""
    from click.testing import CliRunner

    from miio.cloud import cloud

    ci = mocker.Mock()
    ci.get_devices.return_value = {}
    mocker.patch("miio.cloud.CloudInterface", return_value=ci)

    result = CliRunner().invoke(cloud, ["--qr"], input="de\n")

    assert result.exit_code == 0, result.output
    ci.get_devices.assert_called_once()
