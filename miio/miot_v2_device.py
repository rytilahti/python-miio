import logging

from .device import Device
from .miot_spec_v2 import Access, DeviceSpec

_LOGGER = logging.getLogger(__name__)


class MiotV2Device(Device):
    def __init__(
        self,
        spec: DeviceSpec,
        ip: str = None,
        token: str = None,
        start_id: int = 0,
        debug: int = 0,
        lazy_discover: bool = True,
    ) -> None:
        self.spec = spec
        super().__init__(ip, token, start_id, debug, lazy_discover)

    def get_readable_properties(self, request_props=None) -> list:
        properties = [
            {
                "did": self.generate_did(s.type.name, p.type.name),
                "siid": s.iid,
                "piid": p.iid,
            }
            for s in self.spec.services
            for p in s.properties
            if Access.Read in p.access
            and (request_props is None or (s.type.name, p.type.name) in request_props)
        ]

        def get_props(loaded_props, request_props, retry_count):
            if retry_count < 0 or len(request_props) == 0:
                return loaded_props
            props = self.get_properties(
                request_props, property_getter="get_properties", max_properties=15
            )
            loaded_props = loaded_props + [p for p in props if p["code"] == 0]
            request_props = [p for p in props if p["code"] != 0]
            return get_props(loaded_props, request_props, retry_count - 1)

        return get_props([], properties, 5)

    def set_property(self, service_name, property_name, value):
        service = self.spec.find_service(service_name)
        property = service.find_property(property_name)
        return self.send(
            "set_properties",
            [
                {
                    "did": self.generate_did(service_name, property_name),
                    "siid": service.iid,
                    "piid": property.iid,
                    "value": value,
                }
            ],
        )

    @staticmethod
    def generate_did(service_name, property_name):
        if service_name == property_name:
            return service_name
        else:
            return service_name + "." + property_name
