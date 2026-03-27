from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

from miio.miioprotocol import MiIOProtocol


class TestNeedsHandshake:
    """Tests for _needs_handshake with different configurations."""

    def test_always_needs_handshake_when_not_discovered(self) -> None:
        proto = MiIOProtocol(handshake_timeout=3600)
        assert proto._discovered is False
        assert proto._needs_handshake() is True

    def test_lazy_discover_true_no_rehandshake(self) -> None:
        """lazy_discover=True: after first handshake, never re-handshake."""
        proto = MiIOProtocol(lazy_discover=True)
        proto._discovered = True
        proto._last_handshake = datetime.now(tz=timezone.utc) - timedelta(hours=24)
        assert proto._needs_handshake() is False

    def test_lazy_discover_false_always_rehandshake(self) -> None:
        """lazy_discover=False: always re-handshake (timeout=0)."""
        proto = MiIOProtocol(lazy_discover=False)
        proto._discovered = True
        proto._last_handshake = datetime.now(tz=timezone.utc)
        assert proto._needs_handshake() is True

    def test_handshake_timeout_not_expired(self) -> None:
        proto = MiIOProtocol(handshake_timeout=60)
        proto._discovered = True
        proto._last_handshake = datetime.now(tz=timezone.utc) - timedelta(seconds=30)
        assert proto._needs_handshake() is False

    def test_handshake_timeout_expired(self) -> None:
        proto = MiIOProtocol(handshake_timeout=60)
        proto._discovered = True
        proto._last_handshake = datetime.now(tz=timezone.utc) - timedelta(seconds=90)
        assert proto._needs_handshake() is True

    def test_handshake_timeout_zero_always_rehandshake(self) -> None:
        proto = MiIOProtocol(handshake_timeout=0)
        proto._discovered = True
        proto._last_handshake = datetime.now(tz=timezone.utc)
        assert proto._needs_handshake() is True

    def test_handshake_timeout_overrides_lazy_discover(self) -> None:
        """Explicit handshake_timeout takes precedence over lazy_discover."""
        proto = MiIOProtocol(lazy_discover=True, handshake_timeout=10)
        proto._discovered = True
        proto._last_handshake = datetime.now(tz=timezone.utc) - timedelta(seconds=20)
        assert proto._needs_handshake() is True

    def test_no_last_handshake_recorded(self) -> None:
        """Should need handshake if discovered but no timestamp recorded."""
        proto = MiIOProtocol(handshake_timeout=60)
        proto._discovered = True
        proto._last_handshake = None
        assert proto._needs_handshake() is True


class TestHandshakeTimestamp:
    """Tests that send_handshake records _last_handshake and send uses it."""

    def test_send_handshake_records_timestamp(self) -> None:
        """send_handshake should set _last_handshake to current time."""
        proto = MiIOProtocol("127.0.0.1", handshake_timeout=60)
        assert proto._last_handshake is None

        mock_msg: MagicMock = MagicMock()
        mock_msg.header.value.device_id = b"\x01\x02\x03\x04"
        mock_msg.header.value.ts = datetime.now(tz=timezone.utc)
        mock_msg.checksum = b"\x00" * 16

        before: datetime = datetime.now(tz=timezone.utc)
        with patch.object(MiIOProtocol, "discover", return_value=mock_msg):
            proto.send_handshake()
        after: datetime = datetime.now(tz=timezone.utc)

        assert proto._last_handshake is not None
        assert before <= proto._last_handshake <= after
        assert proto._discovered is True

    def test_send_calls_handshake_when_needed(self) -> None:
        """send() should call send_handshake when _needs_handshake is True."""
        proto = MiIOProtocol("127.0.0.1", handshake_timeout=0)
        proto._discovered = True
        proto._last_handshake = datetime.now(tz=timezone.utc)

        with patch.object(proto, "send_handshake") as mock_hs, \
             patch.object(proto, "_create_request", return_value={"id": 1}), \
             patch("socket.socket") as mock_sock:
            mock_instance: MagicMock = mock_sock.return_value
            mock_instance.recvfrom.side_effect = OSError("mocked")
            try:
                proto.send("test_cmd", retry_count=0)
            except Exception:
                pass
            mock_hs.assert_called_once()

    def test_send_skips_handshake_when_not_needed(self) -> None:
        """send() should not call send_handshake when timeout hasn't expired."""
        proto = MiIOProtocol("127.0.0.1", handshake_timeout=3600)
        proto._discovered = True
        proto._last_handshake = datetime.now(tz=timezone.utc)
        proto._device_id = b"\x01\x02\x03\x04"

        with patch.object(proto, "send_handshake") as mock_hs, \
             patch.object(proto, "_create_request", return_value={"id": 1}), \
             patch("socket.socket") as mock_sock:
            mock_instance: MagicMock = mock_sock.return_value
            mock_instance.recvfrom.side_effect = OSError("mocked")
            try:
                proto.send("test_cmd", retry_count=0)
            except Exception:
                pass
            mock_hs.assert_not_called()
