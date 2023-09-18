"""Module implementing handling of miot schema files."""
import json
import logging
from datetime import datetime, timedelta, timezone
from operator import attrgetter
from pathlib import Path
from typing import Dict, List, Optional

import appdirs
from micloud.miotspec import MiotSpec

try:
    from pydantic.v1 import BaseModel, Field
except ImportError:
    from pydantic import BaseModel, Field

from miio import CloudException
from miio.miot_models import DeviceModel

_LOGGER = logging.getLogger(__name__)


class ReleaseInfo(BaseModel):
    """Information about individual miotspec release."""

    model: str
    status: Optional[str]  # only available on full listing
    type: str
    version: int

    @property
    def filename(self) -> str:
        return f"{self.model}_{self.status}_{self.version}.json"


class ReleaseList(BaseModel):
    """Model for miotspec release list."""

    releases: List[ReleaseInfo] = Field(alias="instances")

    def info_for_model(self, model: str, *, status_filter="released") -> ReleaseInfo:
        releases = [inst for inst in self.releases if inst.model == model]

        if not releases:
            raise CloudException(
                f"No releases found for {model=} with {status_filter=}"
            )
        elif len(releases) > 1:
            _LOGGER.warning(
                "%s versions found for model %s: %s, using the newest one",
                len(releases),
                model,
                releases,
            )

        newest_release = max(releases, key=attrgetter("version"))
        _LOGGER.debug("Using %s", newest_release)

        return newest_release


class MiotCloud:
    """Interface for miotspec data."""

    MODEL_MAPPING_FILE = "model-to-urn.json"

    def __init__(self):
        self._cache_dir = Path(appdirs.user_cache_dir("python-miio"))

    def get_release_list(self) -> ReleaseList:
        """Fetch a list of available releases."""
        cache_file = self._cache_dir / MiotCloud.MODEL_MAPPING_FILE
        try:
            mapping = self._file_from_cache(cache_file)
            return ReleaseList.parse_obj(mapping)
        except FileNotFoundError:
            _LOGGER.debug("Did not found non-stale %s, trying to fetch", cache_file)

        specs = MiotSpec.get_specs()
        self._write_to_cache(cache_file, specs)

        return ReleaseList.parse_obj(specs)

    def get_device_model(self, model: str) -> DeviceModel:
        """Get device model for model name."""
        file = self._cache_dir / f"{model}.json"
        try:
            spec = self._file_from_cache(file)
            return DeviceModel.parse_obj(spec)
        except FileNotFoundError:
            _LOGGER.debug("Unable to find schema file %s, going to fetch" % file)

        return DeviceModel.parse_obj(self.get_model_schema(model))

    def get_model_schema(self, model: str) -> Dict:
        """Get the preferred schema for the model."""
        specs = self.get_release_list()
        release_info = specs.info_for_model(model)

        model_file = self._cache_dir / f"{release_info.model}.json"
        try:
            spec = self._file_from_cache(model_file)
            return spec
        except FileNotFoundError:
            _LOGGER.debug(f"Cached schema not found for {model}, going to fetch it")

        spec = MiotSpec.get_spec_for_urn(device_urn=release_info.type)
        self._write_to_cache(model_file, spec)

        return spec

    def _write_to_cache(self, file: Path, data: Dict):
        """Write given *data* to cache file *file*."""
        file.parent.mkdir(parents=True, exist_ok=True)
        written = file.write_text(json.dumps(data))
        _LOGGER.debug("Written %s bytes to %s", written, file)

    def _file_from_cache(self, file, cache_hours=6) -> Dict:
        def _valid_cache():
            expiration = timedelta(hours=cache_hours)
            if datetime.fromtimestamp(
                file.stat().st_mtime, tz=timezone.utc
            ) + expiration > datetime.now(tz=timezone.utc):
                return True

            return False

        if file.exists() and _valid_cache():
            _LOGGER.debug("Cache hit, returning contents of %s", file)
            return json.loads(file.read_text())

        raise FileNotFoundError("Cache file %s not found or it is stale" % file)
