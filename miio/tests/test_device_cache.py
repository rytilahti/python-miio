import json
from pathlib import Path

import pytest

from miio.device_cache import DeviceState, _cache_path, read_cache, write_cache


@pytest.fixture()
def cache_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Override CACHE_DIR to use a temporary directory."""
    monkeypatch.setattr("miio.device_cache.CACHE_DIR", tmp_path)
    return tmp_path


class TestCachePath:
    def test_ipv4_produces_valid_path(self, cache_dir: Path) -> None:
        path = _cache_path("192.168.1.1")
        assert path.parent == cache_dir
        assert path.suffix == ".json"

    def test_ipv6_produces_valid_path(self, cache_dir: Path) -> None:
        path = _cache_path("fe80::1")
        assert path.parent == cache_dir
        assert path.suffix == ".json"
        assert ":" not in path.name

    def test_different_ips_get_different_paths(self, cache_dir: Path) -> None:
        assert _cache_path("192.168.1.1") != _cache_path("192.168.1.2")

    def test_same_ip_gets_same_path(self, cache_dir: Path) -> None:
        assert _cache_path("192.168.1.1") == _cache_path("192.168.1.1")


class TestReadCache:
    def test_missing_file_returns_zero(self, cache_dir: Path) -> None:
        state: DeviceState = read_cache("192.168.1.1")
        assert state["seq"] == 0

    def test_reads_written_data(self, cache_dir: Path) -> None:
        write_cache("192.168.1.1", DeviceState(seq=42))
        state: DeviceState = read_cache("192.168.1.1")
        assert state["seq"] == 42

    def test_corrupt_json_returns_zero(self, cache_dir: Path) -> None:
        path = _cache_path("192.168.1.1")
        path.write_text("not json")
        state: DeviceState = read_cache("192.168.1.1")
        assert state["seq"] == 0

    def test_missing_seq_key_returns_zero(self, cache_dir: Path) -> None:
        path = _cache_path("192.168.1.1")
        path.write_text(json.dumps({"other": 123}))
        state: DeviceState = read_cache("192.168.1.1")
        assert state["seq"] == 0

    def test_non_int_seq_returns_zero(self, cache_dir: Path) -> None:
        path = _cache_path("192.168.1.1")
        path.write_text(json.dumps({"seq": "not_a_number"}))
        state: DeviceState = read_cache("192.168.1.1")
        assert state["seq"] == 0


class TestWriteCache:
    def test_creates_directory(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        nested = tmp_path / "sub" / "dir"
        monkeypatch.setattr("miio.device_cache.CACHE_DIR", nested)
        write_cache("192.168.1.1", DeviceState(seq=5))
        assert nested.exists()

    def test_overwrites_existing(self, cache_dir: Path) -> None:
        write_cache("192.168.1.1", DeviceState(seq=10))
        write_cache("192.168.1.1", DeviceState(seq=20))
        state: DeviceState = read_cache("192.168.1.1")
        assert state["seq"] == 20

    def test_written_file_is_valid_json(self, cache_dir: Path) -> None:
        write_cache("192.168.1.1", DeviceState(seq=99))
        path = _cache_path("192.168.1.1")
        data: dict = json.loads(path.read_text())
        assert data == {"seq": 99}
