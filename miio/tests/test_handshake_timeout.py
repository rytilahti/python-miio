from datetime import datetime, timedelta, timezone

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
