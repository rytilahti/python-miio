import json
import logging
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from miio import CloudException
from miio.miot_cloud import MiotCloud, ReleaseInfo, ReleaseList


def load_fixture(filename: str) -> str:
    """Load a fixture."""
    # TODO: refactor to avoid code duplication
    file = Path(__file__).parent.absolute() / "fixtures" / filename
    with file.open() as f:
        return json.load(f)


@pytest.fixture(scope="module")
def miotspec_releases() -> ReleaseList:
    return ReleaseList.parse_obj(load_fixture("micloud_miotspec_releases.json"))


def test_releaselist(miotspec_releases: ReleaseList):
    assert len(miotspec_releases.releases) == 3


def test_releaselist_single_release(miotspec_releases: ReleaseList):
    wanted_model = "vendor.plug.single_release"
    info: ReleaseInfo = miotspec_releases.info_for_model(wanted_model)
    assert info.model == wanted_model
    assert (
        info.type == "urn:miot-spec-v2:device:outlet:0000xxxx:vendor-single-release:1"
    )


def test_releaselist_multiple_releases(miotspec_releases: ReleaseList):
    """Test that the newest version gets picked."""
    two_releases = miotspec_releases.info_for_model("vendor.plug.two_releases")
    assert two_releases.version == 2
    assert (
        two_releases.type
        == "urn:miot-spec-v2:device:outlet:0000xxxx:vendor-two-releases:2"
    )


def test_releaselist_missing_model(miotspec_releases: ReleaseList):
    """Test that missing release causes an expected exception."""
    with pytest.raises(CloudException):
        miotspec_releases.info_for_model("foo.bar")


def test_get_release_list(
    tmp_path: Path, mocker: MockerFixture, caplog: pytest.LogCaptureFixture
):
    """Test that release list parsing works."""
    caplog.set_level(logging.DEBUG)
    ci = MiotCloud()
    ci._cache_dir = tmp_path

    get_specs = mocker.patch("micloud.miotspec.MiotSpec.get_specs", autospec=True)
    get_specs.return_value = load_fixture("micloud_miotspec_releases.json")

    # Initial call should download the file, and log the cache miss
    releases = ci.get_release_list()
    assert len(releases.releases) == 3
    assert get_specs.called
    assert "Did not found non-stale" in caplog.text

    # Second call should return the data from cache
    caplog.clear()
    get_specs.reset_mock()

    releases = ci.get_release_list()
    assert len(releases.releases) == 3
    assert not get_specs.called
    assert "Did not found non-stale" not in caplog.text


def test_write_to_cache(tmp_path: Path):
    """Test that cache writes and reads function."""
    file_path = tmp_path / "long" / "path" / "example.json"
    ci = MiotCloud()
    ci._write_to_cache(file_path, {"example": "data"})
    data = ci._file_from_cache(file_path)
    assert data["example"] == "data"


def test_read_nonexisting_cache_file(tmp_path: Path):
    """Test that cache reads return None if the file does not exist."""
    file_path = tmp_path / "long" / "path" / "example.json"
    ci = MiotCloud()
    with pytest.raises(FileNotFoundError):
        ci._file_from_cache(file_path)
