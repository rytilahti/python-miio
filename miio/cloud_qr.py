"""QR code login for the Xiaomi cloud.

Xiaomi began serving a captcha on third-party password logins, which the
``micloud`` password flow cannot answer, so :class:`~miio.cloud.CloudInterface`
fails with ``MiCloudAccessDenied`` even when the credentials are correct
(see issue #2038).

Xiaomi's QR code flow is unaffected. The account page issues a QR code, the
user scans it in the Xiaomi Home app, and a long poll returns the session. This
module implements that flow and the signed device-list call, exposing the same
two methods :class:`~miio.cloud.CloudInterface` needs from ``micloud``:
:meth:`login` and :meth:`get_devices`.

It also never handles the account password, which removes a class of problem
rather than working around one.

The request signing follows the scheme documented by
`Xiaomi-cloud-tokens-extractor <https://github.com/PiotrMachowski/Xiaomi-cloud-tokens-extractor>`_
(MIT).
"""

import base64
import hashlib
import json
import logging
import os
import secrets
import time
from collections.abc import Callable
from typing import Any

import requests

from miio.exceptions import CloudException

_LOGGER = logging.getLogger(__name__)

LOGIN_URL = "https://account.xiaomi.com/longPolling/loginUrl"

#: Seconds to wait for the user to scan, if Xiaomi does not say otherwise.
DEFAULT_SCAN_TIMEOUT = 300


def _rc4(key: bytes, data: bytes) -> bytes:
    """RC4, with the first 1024 keystream bytes discarded as Xiaomi expects.

    Implemented here rather than pulled from a crypto library on purpose:
    ``cryptography`` moved ARC4 into ``hazmat.decrepit`` in 43.0, so it is not
    reachable at a stable import path across the versions this package
    supports, and RC4 is a handful of lines. This is Xiaomi's transport
    obfuscation, not a security boundary.
    """
    s = list(range(256))
    j = 0
    for i in range(256):
        j = (j + s[i] + key[i % len(key)]) & 0xFF
        s[i], s[j] = s[j], s[i]

    out = bytearray()
    i = j = 0
    for byte in b"\x00" * 1024 + data:
        i = (i + 1) & 0xFF
        j = (j + s[i]) & 0xFF
        s[i], s[j] = s[j], s[i]
        out.append(byte ^ s[(s[i] + s[j]) & 0xFF])
    return bytes(out[1024:])


def _strip_prefix(text: str) -> dict:
    """Xiaomi prefixes its JSON responses with a fixed guard string."""
    return json.loads(text.replace("&&&START&&&", ""))


def print_qr_to_terminal(png: bytes, login_url: str) -> None:
    """Default QR presenter: write the PNG to a temp file and print the URL.

    Flushed explicitly, because the caller then blocks on a long poll for up to
    five minutes. Without the flush, a redirected or piped stdout would hold
    the instructions in its buffer and the user would sit looking at nothing.
    """
    import tempfile

    path = os.path.join(tempfile.gettempdir(), "miio-cloud-login-qr.png")
    with open(path, "wb") as handle:
        handle.write(png)

    _LOGGER.info("Login QR code written to %s", path)
    print(  # noqa: T201
        f"Scan this QR code with the Xiaomi Home app: {path}\n"
        f"Or open this URL and sign in: {login_url}",
        flush=True,
    )


class QrCodeLogin:
    """Xiaomi cloud session authenticated by scanning a QR code.

    Drop-in for the parts of ``micloud.MiCloud`` that
    :class:`~miio.cloud.CloudInterface` uses.

    Example::

        backend = QrCodeLogin()
        backend.login()
        devices = backend.get_devices(country="de")

    :param on_qr: called with ``(png_bytes, login_url)`` when the code is
        ready. Defaults to writing the PNG to a temporary file and printing
        both paths.
    :param scan_timeout: override how long to wait for the scan.
    """

    def __init__(
        self,
        on_qr: Callable[[bytes, str], None] | None = None,
        scan_timeout: int | None = None,
    ) -> None:
        self._session = requests.Session()
        self._on_qr = on_qr or print_qr_to_terminal
        self._scan_timeout = scan_timeout

        agent_id = "".join(secrets.choice("ABCDE") for _ in range(13))
        self._agent = (
            f"Android-7.1.1-1.0.0-ONEPLUS A3010-136-{agent_id} "
            "APP/xiaomi.smarthome APPV/62830"
        )

        self.user_id: str | None = None
        self._ssecurity: str | None = None
        self._service_token: str | None = None

    @staticmethod
    def api_url(country: str) -> str:
        """Return the API base for a locale. Mainland China has no prefix."""
        prefix = "" if country == "cn" else f"{country}."
        return f"https://{prefix}api.io.mi.com/app"

    # -- login -----------------------------------------------------------

    def login(self) -> bool:
        """Run the QR login. Blocks until the code is scanned or expires."""
        try:
            response = self._session.get(
                LOGIN_URL,
                params={
                    "_qrsize": "480",
                    "qs": "%3Fsid%3Dxiaomiio%26_json%3Dtrue",
                    "callback": "https://sts.api.io.mi.com/sts",
                    "_hasLogo": "false",
                    "sid": "xiaomiio",
                    "serviceParam": "",
                    "_locale": "en_GB",
                    "_dc": str(int(time.time() * 1000)),
                },
                timeout=20,
            )
        except requests.RequestException as ex:
            raise CloudException(f"Unable to request a login QR code: {ex}") from ex

        data = _strip_prefix(response.text) if response.status_code == 200 else {}
        if "qr" not in data:
            raise CloudException("Xiaomi did not return a login QR code")

        timeout = self._scan_timeout or int(data.get("timeout", DEFAULT_SCAN_TIMEOUT))
        png = self._session.get(data["qr"], timeout=20).content
        self._on_qr(png, data["loginUrl"])

        session = self._long_poll(data["lp"], timeout)
        self.user_id = session["userId"]
        self._ssecurity = session["ssecurity"]
        self._service_token = self._service_token_for(session["location"])
        _LOGGER.debug("Logged in as %s", self.user_id)
        return True

    def _long_poll(self, url: str, timeout: int) -> dict:
        """Wait for the user to approve the code in the Xiaomi Home app."""
        started = time.monotonic()
        while time.monotonic() - started < timeout:
            try:
                response = self._session.get(url, timeout=15)
            except requests.Timeout:
                continue  # the long poll cycling is normal, keep waiting
            except requests.RequestException as ex:
                raise CloudException(f"Login polling failed: {ex}") from ex
            if response.status_code == 200:
                return _strip_prefix(response.text)

        raise CloudException("The QR code expired before it was scanned")

    def _service_token_for(self, location: str) -> str:
        try:
            response = self._session.get(
                location,
                headers={"content-type": "application/x-www-form-urlencoded"},
                timeout=20,
            )
        except requests.RequestException as ex:
            raise CloudException(f"Unable to fetch the service token: {ex}") from ex

        token = response.cookies.get("serviceToken")
        if not token:
            raise CloudException("No service token in Xiaomi's response")
        return token

    # -- signing ---------------------------------------------------------

    @staticmethod
    def _signed_nonce(ssecurity: str, nonce: str) -> str:
        digest = hashlib.sha256(
            base64.b64decode(ssecurity) + base64.b64decode(nonce)
        ).digest()
        return base64.b64encode(digest).decode()

    @staticmethod
    def _nonce() -> str:
        minutes = int(time.time() * 1000) // 60000
        return base64.b64encode(os.urandom(8) + minutes.to_bytes(4, "big")).decode()

    @classmethod
    def _signature(cls, url: str, signed_nonce: str, params: dict) -> str:
        parts = ["POST", url.split("com")[1].replace("/app/", "/")]
        parts += [f"{key}={value}" for key, value in params.items()]
        parts.append(signed_nonce)
        return base64.b64encode(
            hashlib.sha1("&".join(parts).encode()).digest()  # noqa: S324
        ).decode()

    @classmethod
    def _seal(cls, signed_nonce: str, text: str) -> str:
        return base64.b64encode(
            _rc4(base64.b64decode(signed_nonce), text.encode())
        ).decode()

    @classmethod
    def _unseal(cls, signed_nonce: str, text: str) -> bytes:
        """Decrypt a response.

        The base64 decode is required; feeding the raw response body to RC4
        yields bytes that are not valid UTF-8.
        """
        return _rc4(base64.b64decode(signed_nonce), base64.b64decode(text))

    def _post(self, country: str, path: str, data: str) -> dict | None:
        if not (self._service_token and self._ssecurity):
            raise CloudException("Not logged in")

        url = self.api_url(country) + path
        nonce = self._nonce()
        signed = self._signed_nonce(self._ssecurity, nonce)

        fields: dict[str, Any] = {"data": data}
        fields["rc4_hash__"] = self._signature(url, signed, fields)
        for key, value in list(fields.items()):
            fields[key] = self._seal(signed, value)
        fields["signature"] = self._signature(url, signed, fields)
        fields["ssecurity"] = self._ssecurity
        fields["_nonce"] = nonce

        try:
            response = self._session.post(
                url,
                params=fields,
                headers={
                    "Accept-Encoding": "identity",
                    "User-Agent": self._agent,
                    "Content-Type": "application/x-www-form-urlencoded",
                    "x-xiaomi-protocal-flag-cli": "PROTOCAL-HTTP2",
                    "MIOT-ENCRYPT-ALGORITHM": "ENCRYPT-RC4",
                },
                cookies={
                    "userId": str(self.user_id),
                    "yetAnotherServiceToken": self._service_token,
                    "serviceToken": self._service_token,
                    "locale": "en_GB",
                    "channel": "MI_APP_STORE",
                },
                timeout=25,
            )
        except requests.RequestException as ex:
            raise CloudException(f"Cloud request failed: {ex}") from ex

        if response.status_code != 200:
            _LOGGER.debug("%s returned HTTP %s", path, response.status_code)
            return None
        try:
            return json.loads(self._unseal(signed, response.text))
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
            _LOGGER.debug("Unable to decode the response for %s", path)
            return None

    # -- devices ---------------------------------------------------------

    def get_devices(self, country: str = "cn") -> list[dict]:
        """Return the raw device list for a locale.

        Deliberately calls the same endpoint as ``micloud.MiCloud.get_devices``
        and returns the same records, so this is a drop-in replacement and
        :class:`~miio.cloud.CloudDeviceInfo` parses the result unchanged.
        """
        response = self._post(
            country,
            "/home/device_list",
            '{"getVirtualModel":false,"getHuamiDevices":0}',
        )
        return ((response or {}).get("result") or {}).get("list") or []
