import enum
import re
from typing import Dict, Optional


class FilterType(enum.Enum):
    Regular = "regular"
    AntiBacterial = "anti-bacterial"
    AntiFormaldehyde = "anti-formaldehyde"
    Unknown = "unknown"


FILTER_TYPE_RE = (
    (re.compile(r"^\d+:\d+:41:30$"), FilterType.AntiBacterial),
    (re.compile(r"^\d+:\d+:(30|0|00):31$"), FilterType.AntiFormaldehyde),
    (re.compile(r".*"), FilterType.Regular),
)


class FilterTypeUtil:
    """Utility class for determining xiaomi air filter type."""

    _filter_type_cache: Dict[str, Optional[FilterType]] = {}

    def determine_filter_type(
        self, rfid_tag: Optional[str], product_id: Optional[str]
    ) -> Optional[FilterType]:
        """Determine Xiaomi air filter type based on its product ID.

        :param rfid_tag: RFID tag value
        :param product_id: Product ID such as "0:0:30:33"
        """
        if rfid_tag is None:
            return None
        if rfid_tag == "0:0:0:0:0:0:0":
            return FilterType.Unknown
        if product_id is None:
            return FilterType.Regular

        ft = self._filter_type_cache.get(product_id)
        if ft is None:
            for filter_re, filter_type in FILTER_TYPE_RE:
                if filter_re.match(product_id):
                    ft = self._filter_type_cache[product_id] = filter_type
                    break
        return ft
