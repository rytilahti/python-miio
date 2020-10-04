import logging
from typing import Any, Dict

from .click_common import command, format_output
from .device import Device

_LOGGER = logging.getLogger(__name__)


class WaterPurifierYunmiStatus:
    """Container for status reports from the water purifier (Yunmi model)."""

    def __init__(self, data: Dict[str, Any]) -> None:
        self.data = data

    @property
    def run_status(self) -> int:
        """Current running status, 0 for no error."""
        return self.data["run_status"]

    @property
    def f1_totaltime(self) -> int:
        """Filter1 total available time in hours."""
        return self.data["f1_totaltime"]

    @property
    def f1_usedtime(self) -> int:
        """Filter1 used time in hours."""
        return self.data["f1_usedtime"]

    @property
    def f1_totalflow(self) -> int:
        """Filter1 total available flow in Metric Liter (L)."""
        return self.data["f1_totalflow"]

    @property
    def f1_usedflow(self) -> int:
        """Filter1 used flow in Metric Liter (L)."""
        return self.data["f1_usedflow"]

    @property
    def f2_totaltime(self) -> int:
        """Filter2 total available time in hours."""
        return self.data["f2_totaltime"]

    @property
    def f2_usedtime(self) -> int:
        """Filter2 used time in hours."""
        return self.data["f2_usedtime"]

    @property
    def f2_totalflow(self) -> int:
        """Filter2 total available flow in Metric Liter (L)."""
        return self.data["f2_totalflow"]

    @property
    def f2_usedflow(self) -> int:
        """Filter2 used flow in Metric Liter (L)."""
        return self.data["f2_usedflow"]

    @property
    def f3_totaltime(self) -> int:
        """Filter3 total available time in hours."""
        return self.data["f3_totaltime"]

    @property
    def f3_usedtime(self) -> int:
        """Filter3 used time in hours."""
        return self.data["f3_usedtime"]

    @property
    def f3_totalflow(self) -> int:
        """Filter3 total available flow in Metric Liter (L)."""
        return self.data["f3_totalflow"]

    @property
    def f3_usedflow(self) -> int:
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
            "run_status=%s, "
            "f1_totaltime=%s, "
            "f1_usedtime=%s, "
            "f1_totalflow=%s, "
            "f1_usedflow=%s, "
            "f2_totaltime=%s, "
            "f2_usedtime=%s, "
            "f2_totalflow=%s, "
            "f2_usedflow=%s, "
            "f3_totaltime=%s, "
            "f3_usedtime=%s, "
            "f3_totalflow=%s, "
            "f3_usedflow=%s, "
            "tds_in=%s, "
            "tds_out=%s, "
            "rinse=%s, "
            "temperature=%s, "
            "tds_warn_thd=%s>"
            % (
                self.run_status,
                self.f1_totaltime,
                self.f1_usedtime,
                self.f1_totalflow,
                self.f1_usedflow,
                self.f2_totaltime,
                self.f2_usedtime,
                self.f2_totalflow,
                self.f2_usedflow,
                self.f3_totaltime,
                self.f3_usedtime,
                self.f3_totalflow,
                self.f3_usedflow,
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
            ""
            "Error: {result.run_status}\n"
            "Filter1 total time: {result.f1_totaltime} hours\n"
            "Filter1 used time: {result.f1_usedtime} hours\n"
            "Filter1 total flow: {result.f1_totalflow} L\n"
            "Filter1 used flow: {result.f1_usedflow} L\n"
            "Filter2 total time: {result.f2_totaltime} hours\n"
            "Filter2 used time: {result.f2_usedtime} hours\n"
            "Filter2 total flow: {result.f2_totalflow} L\n"
            "Filter2 used flow: {result.f2_usedflow} L\n"
            "Filter3 total time: {result.f3_totaltime} hours\n"
            "Filter3 used time: {result.f3_usedtime} hours\n"
            "Filter3 total flow: {result.f3_totalflow} L\n"
            "Filter3 used flow: {result.f3_usedflow} L\n"
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
            # "mode",
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
            # "tds_out_avg",
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
