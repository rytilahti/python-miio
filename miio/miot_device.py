import logging

from .device import Device

_LOGGER = logging.getLogger(__name__)


class MiotDevice(Device):
    """Main class representing a MIoT device."""

    def __init__(
        self,
        mapping: dict,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
    ) -> None:
        self.mapping = mapping
        super().__init__(ip, token, start_id, debug, lazy_discover)

    def get_properties(self) -> list:
        """Retrieve raw properties based on mapping."""

        # We send property key in "did" because it's sent back via response and we can identify the property.
        properties = [{"did": k, **v} for k, v in self.mapping.items()]

        # A single request is limited to 16 properties. Therefore the
        # properties are divided into multiple requests
        _props = properties.copy()
        values = []
        while _props:
            values.extend(self.send("get_properties", _props[:15]))
            _props[:] = _props[15:]

        properties_count = len(properties)
        values_count = len(values)
        if properties_count != values_count:
            _LOGGER.debug(
                "Count (%s) of requested properties does not match the "
                "count (%s) of received values.",
                properties_count,
                values_count,
            )

        return values

    def set_property(self, property_key: str, value):
        """Sets property value."""

        return self.send(
            "set_properties",
            [{"did": property_key, **self.mapping[property_key], "value": value}],
        )
