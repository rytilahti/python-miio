"""Module implementing handling of miot schema files."""
import json
import logging
from datetime import datetime, timedelta
from operator import attrgetter
from pathlib import Path
from typing import Dict, List, Optional

import appdirs
from micloud.miotspec import MiotSpec
from pydantic import BaseModel, Field

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
            raise Exception(f"No releases found for {model=} with {status_filter=}")
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

    def __init__(self):
        self._cache_dir = Path(appdirs.user_cache_dir("python-miio"))

    def get_device_model(self, model: str) -> DeviceModel:
        """Get device model for model name."""
        file = self._cache_dir / f"{model}.json"
        spec = self._file_from_cache(file)
        if spec is not None:
            return DeviceModel.parse_obj(spec)

        return DeviceModel.parse_obj(self.get_model_schema(model))

    def get_model_schema(self, model: str) -> Dict:
        """Get the preferred schema for the model."""
        specs = self.get_release_list()
        release_info = specs.info_for_model(model)

        model_file = self._cache_dir / f"{release_info.model}.json"
        spec = self._file_from_cache(model_file)
        if spec is not None:
            return spec

        spec = MiotSpec.get_spec_for_urn(device_urn=release_info.type)
        self._write_to_cache(model_file, spec)

        return spec

    def _write_to_cache(self, file: Path, data: Dict):
        """Write given *data* to cache file *file*."""
        file.parent.mkdir(exist_ok=True)
        written = file.write_text(json.dumps(data))
        _LOGGER.debug("Written %s bytes to %s", written, file)

    def _file_from_cache(self, file, cache_hours=6) -> Optional[Dict]:
        def _valid_cache():
            expiration = timedelta(hours=cache_hours)
            if (
                datetime.fromtimestamp(file.stat().st_mtime) + expiration
                > datetime.utcnow()
            ):
                return True

            return False

        if file.exists() and _valid_cache():
            _LOGGER.debug("Returning data from cache file %s", file)
            return json.loads(file.read_text())

        _LOGGER.debug("Cache file %s not found or it is stale", file)
        return None

    def get_release_list(self) -> ReleaseList:
        """Fetch a list of available releases."""
        mapping_file = "model-to-urn.json"

        cache_file = self._cache_dir / mapping_file
        mapping = self._file_from_cache(cache_file)
        if mapping is not None:
            return ReleaseList.parse_obj(mapping)

        specs = MiotSpec.get_specs()
        self._write_to_cache(cache_file, specs)

        return ReleaseList.parse_obj(specs)
