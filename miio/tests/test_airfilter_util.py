from unittest import TestCase

import pytest

from miio.airfilter_util import FilterType, FilterTypeUtil


@pytest.fixture(scope="class")
def airfilter_util(request):
    request.cls.filter_type_util = FilterTypeUtil()


@pytest.mark.usefixtures("airfilter_util")
class TestAirFilterUtil(TestCase):
    def test_determine_filter_type__recognises_unknown_filter(self):
        assert (
            self.filter_type_util.determine_filter_type("0:0:0:0:0:0:0", None)
            is FilterType.Unknown
        )

    def test_determine_filter_type__recognises_antibacterial_filter(self):
        assert (
            self.filter_type_util.determine_filter_type(
                "80:64:d1:ba:4f:5f:4", "12:34:41:30"
            )
            is FilterType.AntiBacterial
        )

    def test_determine_filter_type__recognises_antiformaldehyde_filter(self):
        assert (
            self.filter_type_util.determine_filter_type(
                "80:64:d1:ba:4f:5f:4", "12:34:00:31"
            )
            is FilterType.AntiFormaldehyde
        )

    def test_determine_filter_type__falls_back_to_regular_filter(self):
        regular_filters = [
            "12:34:56:78",
            "12:34:56:31",
            "12:34:56:31:11:11",
            "CO:FF:FF:EE",
            None,
        ]
        for product_id in regular_filters:
            assert (
                self.filter_type_util.determine_filter_type(
                    "80:64:d1:ba:4f:5f:4", product_id
                )
                is FilterType.Regular
            )
