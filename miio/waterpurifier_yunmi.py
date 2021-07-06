import logging
from datetime import timedelta
from typing import Any, Dict, List

from .click_common import command, format_output
from .device import Device, DeviceStatus

_LOGGER = logging.getLogger(__name__)

ERROR_DESCRIPTION = [
    {
        "name": "Water temperature anomaly",
        "advice": "Check if inlet water temperature is among 5~38℃.",
    },
    {
        "name": "Inlet water flow meter damaged",
        "advice": "Try to purify water again after reinstalling the filter for serval times.",
    },
    {
        "name": "Water flow sensor anomaly",
        "advice": "Check if the water pressure is too low.",
    },
    {"name": "Filter life expired", "advice": "Replace filter."},
    {"name": "WiFi communication error", "advice": "Contact the after-sales."},
    {"name": "EEPROM communication error", "advice": "Contact the after-sales."},
    {"name": "RFID communication error", "advice": "Contact the after-sales."},
    {
        "name": "Faucet communication error",
        "advice": "Try to plug in the faucet again.",
    },
    {
        "name": "Purified water flow sensor anomaly",
        "advice": "Check whether all filters are properly installed and water pressure is normal.",
    },
    {
        "name": "Water leak",
        "advice": "Check if there is water leaking around the water purifier.",
    },
    {"name": "Floater anomaly", "advice": "Contact the after-sales."},
    {"name": "TDS anomaly", "advice": "Check if the RO filter is expired."},
    {
        "name": "Water temperature too high",
        "advice": "Check if inlet water is warm water with temperature above 40℃.",
    },
    {
        "name": "Recovery rate anomaly",
        "advice": "Check if the waste water pipe works abnormally and the RO filter is expired.",
    },
    {
        "name": "Outlet water quality anomaly",
        "advice": "Check if the waste water pipe works abnormally and the RO filter is expired.",
    },
    {
        "name": "Thermal protection for pumps",
        "advice": "The water purifier has worked for a long time, please use it after 20 minutes.",
    },
    {
        "name": "Dry burning protection",
        "advice": "Check if the inlet water pipe works abnormally.",
    },
    {
        "name": "Outlet water NTC anomaly",
        "advice": "Switch off the purifier and restart it again.",
    },
    {
        "name": "Dry burning NTC anomaly",
        "advice": "Switch off the purifier and restart it again.",
    },
    {
        "name": "Heater anomaly",
        "advice": "Switch off the purifier and restart it again.",
    },
]


class OperationStatus(DeviceStatus):
    def __init__(self, operation_status: int):
        """Operation status parser.

        Return value of operation_status: <int>

        We should convert the operation_status code to binary, each bit from
        LSB to MSB represents one error. It's able to cover multiple errors.

        Example operation_status value: 9 (binary: 1001)
        Thus, the purifier reports 2 errors, stands bit 0 and bit 3,
        means "Water temperature anomaly" and "Filter life expired".
        """
        self.err_list = [
            ERROR_DESCRIPTION[i]
            for i in range(0, len(ERROR_DESCRIPTION))
            if (1 << i) & operation_status
        ]

    @property
    def errors(self) -> List:
        return self.err_list


class WaterPurifierYunmiStatus(DeviceStatus):
    """Container for status reports from the water purifier (Yunmi model)."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """Status of a Water Purifier C1 (yummi.waterpuri.lx11):

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
    def operation_status(self) -> OperationStatus:
        """Current operation status."""
        return OperationStatus(self.data["run_status"])

    @property
    def filter1_life_total(self) -> timedelta:
        """Filter1 total available time in hours."""
        return timedelta(hours=self.data["f1_totaltime"])

    @property
    def filter1_life_used(self) -> timedelta:
        """Filter1 used time in hours."""
        return timedelta(hours=self.data["f1_usedtime"])

    @property
    def filter1_life_remaining(self) -> timedelta:
        """Filter1 remaining time in hours."""
        return self.filter1_life_total - self.filter1_life_used

    @property
    def filter1_flow_total(self) -> int:
        """Filter1 total available flow in Metric Liter (L)."""
        return self.data["f1_totalflow"]

    @property
    def filter1_flow_used(self) -> int:
        """Filter1 used flow in Metric Liter (L)."""
        return self.data["f1_usedflow"]

    @property
    def filter1_flow_remaining(self) -> int:
        """Filter1 remaining flow in Metric Liter (L)."""
        return self.filter1_flow_total - self.filter1_flow_used

    @property
    def filter2_life_total(self) -> timedelta:
        """Filter2 total available time in hours."""
        return timedelta(hours=self.data["f2_totaltime"])

    @property
    def filter2_life_used(self) -> timedelta:
        """Filter2 used time in hours."""
        return timedelta(hours=self.data["f2_usedtime"])

    @property
    def filter2_life_remaining(self) -> timedelta:
        """Filter2 remaining time in hours."""
        return self.filter2_life_total - self.filter2_life_used

    @property
    def filter2_flow_total(self) -> int:
        """Filter2 total available flow in Metric Liter (L)."""
        return self.data["f2_totalflow"]

    @property
    def filter2_flow_used(self) -> int:
        """Filter2 used flow in Metric Liter (L)."""
        return self.data["f2_usedflow"]

    @property
    def filter2_flow_remaining(self) -> int:
        """Filter2 remaining flow in Metric Liter (L)."""
        return self.filter2_flow_total - self.filter2_flow_used

    @property
    def filter3_life_total(self) -> timedelta:
        """Filter3 total available time in hours."""
        return timedelta(hours=self.data["f3_totaltime"])

    @property
    def filter3_life_used(self) -> timedelta:
        """Filter3 used time in hours."""
        return timedelta(hours=self.data["f3_usedtime"])

    @property
    def filter3_life_remaining(self) -> timedelta:
        """Filter3 remaining time in hours."""
        return self.filter3_life_total - self.filter3_life_used

    @property
    def filter3_flow_total(self) -> int:
        """Filter3 total available flow in Metric Liter (L)."""
        return self.data["f3_totalflow"]

    @property
    def filter3_flow_used(self) -> int:
        """Filter3 used flow in Metric Liter (L)."""
        return self.data["f3_usedflow"]

    @property
    def filter3_flow_remaining(self) -> int:
        """Filter1 remaining flow in Metric Liter (L)."""
        return self.filter3_flow_total - self.filter3_flow_used

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


class WaterPurifierYunmi(Device):
    """Main class representing the water purifier (Yunmi model)."""

    @command(
        default_output=format_output(
            "",
            "Operaton status: {result.operation_status}\n"
            "Filter1 total time: {result.filter1_life_total}\n"
            "Filter1 used time: {result.filter1_life_used}\n"
            "Filter1 remaining time: {result.filter1_life_remaining}\n"
            "Filter1 total flow: {result.filter1_flow_total} L\n"
            "Filter1 used flow: {result.filter1_flow_used} L\n"
            "Filter1 remaining flow: {result.filter1_flow_remaining} L\n"
            "Filter2 total time: {result.filter2_life_total}\n"
            "Filter2 used time: {result.filter2_life_used}\n"
            "Filter2 remaining time: {result.filter2_life_remaining}\n"
            "Filter2 total flow: {result.filter2_flow_total} L\n"
            "Filter2 used flow: {result.filter2_flow_used} L\n"
            "Filter2 remaining flow: {result.filter2_flow_remaining} L\n"
            "Filter3 total time: {result.filter3_life_total}\n"
            "Filter3 used time: {result.filter3_life_used}\n"
            "Filter3 remaining time: {result.filter3_life_remaining}\n"
            "Filter3 total flow: {result.filter3_flow_total} L\n"
            "Filter3 used flow: {result.filter3_flow_used} L\n"
            "Filter3 remaining flow: {result.filter3_flow_remaining} L\n"
            "TDS in: {result.tds_in}\n"
            "TDS out: {result.tds_out}\n"
            "Rinsing: {result.rinse}\n"
            "Temperature: {result.temperature} ℃\n"
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
