import logging
from datetime import timedelta
from typing import Any, Dict

from .click_common import command, format_output
from .device import Device

_LOGGER = logging.getLogger(__name__)


class WaterPurifierYunmiStatus:
    """Container for status reports from the water purifier (Yunmi model)."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Status of a Water Purifier C1 (yummi.waterpuri.lx11):
            [0, 7200, 8640, 520, 379, 7200, 17280, 2110, 4544,
            80, 4, 0, 31, 100, 7200, 8640, 1440, 3313]

        Parsed by WaterPurifierYunmi device as:
            {'run_status': 0, 'filter1_flow_total': 7200, 'filter1_life_total': 8640,
             'filter1_flow_used': 520, 'filter1_life_used': 379, 'filter2_flow_total': 7200,
             'filter2_life_total': 17280, 'filter2_flow_used': 2110, 'filter2_life_used': 4544,
             'tds_in': 80, 'tds_out': 4, 'rinse': 0, 'temperature': 31,
             'tds_warn_thd': 100, 'filter3_flow_total': 7200, 'filter3_life_total': 8640,
             'filter3_flow_used': 1440, 'filter3_life_used': 3313}
        """
        self.data = data

    @property
    def status(self) -> int:
        """Current running status, 0 for no error."""
        return self.data["run_status"]

    @property
    def filter1_life_total(self) -> timedelta:
        """Filter1 total available time in hours."""
        return self.data["f1_totaltime"]

    @property
    def filter1_life_used(self) -> timedelta:
        """Filter1 used time in hours."""
        return self.data["f1_usedtime"]

    @property
    def filter1_flow_total(self) -> int:
        """Filter1 total available flow in Metric Liter (L)."""
        return self.data["f1_totalflow"]

    @property
    def filter1_flow_used(self) -> int:
        """Filter1 used flow in Metric Liter (L)."""
        return self.data["f1_usedflow"]

    @property
    def filter2_life_total(self) -> timedelta:
        """Filter2 total available time in hours."""
        return self.data["f2_totaltime"]

    @property
    def filter2_life_used(self) -> timedelta:
        """Filter2 used time in hours."""
        return self.data["f2_usedtime"]

    @property
    def filter2_flow_total(self) -> int:
        """Filter2 total available flow in Metric Liter (L)."""
        return self.data["f2_totalflow"]

    @property
    def filter2_flow_used(self) -> int:
        """Filter2 used flow in Metric Liter (L)."""
        return self.data["f2_usedflow"]

    @property
    def filter3_life_total(self) -> timedelta:
        """Filter3 total available time in hours."""
        return self.data["f3_totaltime"]

    @property
    def filter3_life_used(self) -> timedelta:
        """Filter3 used time in hours."""
        return self.data["f3_usedtime"]

    @property
    def filter3_flow_total(self) -> int:
        """Filter3 total available flow in Metric Liter (L)."""
        return self.data["f3_totalflow"]

    @property
    def filter3_flow_used(self) -> int:
        """Filter3 used flow in Metric Liter (L)."""
        return self.data["f3_usedflow"]

    @property
    def tds_in(self) -> int:
        """TDS value of input water."""
        return self.data["tds_in"]

    @property
    def tds_out(self) -> int:
        """TDS value of output water."""
        return self.data["tds_out"]

    @property
    def rinse(self) -> bool:
        """True if the device is rinsing."""
        return self.data["rinse"]

    @property
    def temperature(self) -> int:
        """Current water temperature in Celsius."""
        return self.data["temperature"]

    @property
    def tds_warn_thd(self) -> int:
        """TDS warning threshold."""
        return self.data["tds_warn_thd"]

    def __repr__(self) -> str:
        return (
            "<WaterPurifierYunmiStatus "
            "status=%s, "
            "filter1_life_total=%s, "
            "filter1_life_used=%s, "
            "filter1_flow_total=%s, "
            "filter1_flow_used=%s, "
            "filter2_life_total=%s, "
            "filter2_life_used=%s, "
            "filter2_flow_total=%s, "
            "filter2_flow_used=%s, "
            "filter3_life_total=%s, "
            "filter3_life_used=%s, "
            "filter3_flow_total=%s, "
            "filter3_flow_used=%s, "
            "tds_in=%s, "
            "tds_out=%s, "
            "rinse=%s, "
            "temperature=%s, "
            "tds_warn_thd=%s>"
            % (
                self.status,
                self.filter1_life_total,
                self.filter1_life_used,
                self.filter1_flow_total,
                self.filter1_flow_used,
                self.filter2_life_total,
                self.filter2_life_used,
                self.filter2_flow_total,
                self.filter2_flow_used,
                self.filter3_life_total,
                self.filter3_life_used,
                self.filter3_flow_total,
                self.filter3_flow_used,
                self.tds_in,
                self.tds_out,
                self.rinse,
                self.temperature,
                self.tds_warn_thd,
            )
        )

    def __json__(self):
        return self.data


class WaterPurifierYunmi(Device):
    """Main class representing the water purifier (Yunmi model)."""

    @command(
        default_output=format_output(
            "",
            "Error: {result.status}\n"
            "Filter1 total time: {result.filter1_life_total} hours\n"
            "Filter1 used time: {result.filter1_life_used} hours\n"
            "Filter1 total flow: {result.filter1_flow_total} L\n"
            "Filter1 used flow: {result.filter1_flow_used} L\n"
            "Filter2 total time: {result.filter2_life_total} hours\n"
            "Filter2 used time: {result.filter2_life_used} hours\n"
            "Filter2 total flow: {result.filter2_flow_total} L\n"
            "Filter2 used flow: {result.filter2_flow_used} L\n"
            "Filter3 total time: {result.filter3_life_total} hours\n"
            "Filter3 used time: {result.filter3_life_used} hours\n"
            "Filter3 total flow: {result.filter3_flow_total} L\n"
            "Filter3 used flow: {result.filter3_flow_used} L\n"
            "TDS in: {result.tds_in}\n"
            "TDS out: {result.tds_out}\n"
            "Rinsing: {result.rinse}\n"
            "Temperature: {result.temperature}\n"
            "TDS warning threshold: {result.tds_warn_thd}\n",
        )
    )
    def status(self) -> WaterPurifierYunmiStatus:
        """Retrieve properties."""

        properties = [
            "run_status",
            "f1_totalflow",
            "f1_totaltime",
            "f1_usedflow",
            "f1_usedtime",
            "f2_totalflow",
            "f2_totaltime",
            "f2_usedflow",
            "f2_usedtime",
            "tds_in",
            "tds_out",
            "rinse",
            "temperature",
            "tds_warn_thd",
            "f3_totalflow",
            "f3_totaltime",
            "f3_usedflow",
            "f3_usedtime",
        ]

        """
        Some models doesn't support a list of properties, while fetching them one
        per time usually runs into "ack timeout" error. Thus fetch them all at one
        time.
        Key "mode" (always 'purifying') and key "tds_out_avg" (always 0) are not
        included in return values.
        """
        values = self.send("get_prop", ["all"])

        prop_count = len(properties)
        val_count = len(values)
        if prop_count != val_count:
            _LOGGER.debug(
                "Count (%s) of requested properties does not match the "
                "count (%s) of received values.",
                prop_count,
                val_count,
            )

        return WaterPurifierYunmiStatus(dict(zip(properties, values)))
