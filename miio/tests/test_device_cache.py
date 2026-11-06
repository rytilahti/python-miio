import json
from pathlib import Path

import pytest

from miio.device_cache import DeviceState, _cache_path, read_cache, write_cache


@pytest.fixture
def cache_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr("miio.device_cache.CACHE_DIR", tmp_path)
    return tmp_path


def test_cache_path_ipv4(cache_dir: Path) -> None:
    path = _cache_path("192.168.1.1")
    assert path.parent == cache_dir
    assert path.suffix == ".json"


def test_cache_path_ipv6(cache_dir: Path) -> None:
    path = _cache_path("fe80::1")
    assert path.parent == cache_dir
    assert path.suffix == ".json"
    assert ":" not in path.name


def test_cache_path_different_ips(cache_dir: Path) -> None:
    assert _cache_path("192.168.1.1") != _cache_path("192.168.1.2")


def test_cache_path_same_ip(cache_dir: Path) -> None:
    assert _cache_path("192.168.1.1") == _cache_path("192.168.1.1")


def test_read_cache_missing_file(cache_dir: Path) -> None:
    state: DeviceState = read_cache("192.168.1.1")
    assert state["seq"] == 0


def test_read_cache_written_data(cache_dir: Path) -> None:
    write_cache("192.168.1.1", DeviceState(seq=42))
    state: DeviceState = read_cache("192.168.1.1")
    assert state["seq"] == 42


def test_read_cache_corrupt_json(cache_dir: Path) -> None:
    _cache_path("192.168.1.1").write_text("not json")
    state: DeviceState = read_cache("192.168.1.1")
    assert state["seq"] == 0


def test_read_cache_missing_seq_key(cache_dir: Path) -> None:
    _cache_path("192.168.1.1").write_text(json.dumps({"other": 123}))
    state: DeviceState = read_cache("192.168.1.1")
    assert state["seq"] == 0


def test_read_cache_non_int_seq(cache_dir: Path) -> None:
    _cache_path("192.168.1.1").write_text(json.dumps({"seq": "not_a_number"}))
    state: DeviceState = read_cache("192.168.1.1")
    assert state["seq"] == 0


def test_write_cache_creates_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    nested = tmp_path / "sub" / "dir"
    monkeypatch.setattr("miio.device_cache.CACHE_DIR", nested)
    write_cache("192.168.1.1", DeviceState(seq=5))
    assert nested.exists()


def test_write_cache_overwrites_existing(cache_dir: Path) -> None:
    write_cache("192.168.1.1", DeviceState(seq=10))
    write_cache("192.168.1.1", DeviceState(seq=20))
    assert read_cache("192.168.1.1")["seq"] == 20


def test_write_cache_valid_json(cache_dir: Path) -> None:
    write_cache("192.168.1.1", DeviceState(seq=99))
    data: dict = json.loads(_cache_path("192.168.1.1").read_text())
    assert data == {"seq": 99}
