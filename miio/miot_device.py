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

    def get_properties_for_mapping(self) -> list:
        """Retrieve raw properties based on mapping."""

        # We send property key in "did" because it's sent back via response and we can identify the property.
        properties = [{"did": k, **v} for k, v in self.mapping.items()]

        return self.get_properties(
            properties, property_getter="get_properties", max_properties=15
        )
    
    def get_property(self, property_key: str) -> dict:
        """Retrieve raw property based on mapping."""
        property = {"did": property_key, **self.mapping.get(property_key)}

        return self.get_properties(
            [property], property_getter="get_properties", max_properties=1
        )[0]

    def get_value(self, property_key: str):
        """Retrieve a property value based on mapping."""
        return self.get_property(property_key).get("value")

    def set_property(self, property_key: str, value):
        """Sets property value."""

        return self.send(
            "set_properties",
            [{"did": property_key, **self.mapping[property_key], "value": value}],
        )
