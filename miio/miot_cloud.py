"""Module implementing handling of miot schema files."""
import logging
from datetime import datetime, timedelta
from operator import attrgetter
from pathlib import Path
from typing import List

import appdirs
import requests  # TODO: externalize HTTP requests to avoid direct dependency
from pydantic import BaseModel

from miio.miot_models import DeviceModel

_LOGGER = logging.getLogger(__name__)


class ReleaseInfo(BaseModel):
    model: str
    status: str
    type: str
    version: int

    @property
    def filename(self) -> str:
        return f"{self.model}_{self.status}_{self.version}.json"


class ReleaseList(BaseModel):
    instances: List[ReleaseInfo]

    def info_for_model(self, model: str, *, status_filter="released") -> ReleaseInfo:
        matches = [inst for inst in self.instances if inst.model == model]

        if len(matches) > 1:
            _LOGGER.warning(
                "more than a single match for model %s: %s, filtering with status=%s",
                model,
                matches,
                status_filter,
            )

        released_versions = [inst for inst in matches if inst.status == status_filter]
        if not released_versions:
            raise Exception(f"No releases for {model}, adjust status_filter?")

        _LOGGER.debug("Got %s releases, picking the newest one", released_versions)

        match = max(released_versions, key=attrgetter("version"))
        _LOGGER.debug("Using %s", match)

        return match


class MiotCloud:
    def __init__(self):
        self._cache_dir = Path(appdirs.user_cache_dir("python-miio"))

    def get_device_model(self, model: str) -> DeviceModel:
        """Get device model for model name."""
        file = self._cache_dir / f"{model}.json"
        if file.exists():
            _LOGGER.debug("Using cached %s", file)
            return DeviceModel.parse_raw(file.read_text())

        return DeviceModel.parse_raw(self.get_model_schema(model))

    def get_model_schema(self, model: str) -> str:
        """Get the preferred schema for the model."""
        instances = self.fetch_release_list()
        release_info = instances.info_for_model(model)

        model_file = self._cache_dir / f"{release_info.model}.json"
        url = f"https://miot-spec.org/miot-spec-v2/instance?type={release_info.type}"

        data = self._fetch(url, model_file)

        return data

    def fetch_release_list(self):
        """Fetch a list of available schemas."""
        mapping_file = "model-to-urn.json"
        url = "http://miot-spec.org/miot-spec-v2/instances?status=all"
        data = self._fetch(url, self._cache_dir / mapping_file)

        return ReleaseList.parse_raw(data)

    def _fetch(self, url: str, target_file: Path, cache_hours=6):
        """Fetch the URL and cache results, if expired."""

        def valid_cache():
            expiration = timedelta(hours=cache_hours)
            if (
                datetime.fromtimestamp(target_file.stat().st_mtime) + expiration
                > datetime.utcnow()
            ):
                return True

            return False

        if target_file.exists() and valid_cache():
            _LOGGER.debug("Returning data from cache: %s", target_file)
            return target_file.read_text()

        _LOGGER.debug("Going to download %s to %s", url, target_file)
        content = requests.get(url)
        content.raise_for_status()

        response = content.text
        written = target_file.write_text(response)
        _LOGGER.debug("Written %s bytes to %s", written, target_file)

        return response
