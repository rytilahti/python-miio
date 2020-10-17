class DummyMiIOProtocol:
    """
    DummyProtocol allows you mock MiIOProtocol.
    """

    def __init__(self, dummy_device):
        # TODO: Ideally, return_values should be passed in here. Passing in dummy_device (which must have
        #       return_values) is a temporary workaround to minimize diff size.
        self.dummy_device = dummy_device

    def send(self, command: str, parameters=None, retry_count=3, extra_parameters=None):
        """Overridden send() to return values from `self.return_values`."""
        return self.dummy_device.return_values[command](parameters)


class DummyDevice:
    """DummyDevice base class, you should inherit from this and call
    `super().__init__(args, kwargs)` to save the original state.

    This class provides helpers to test simple devices, for more complex
    ones you will want to extend the `return_values` accordingly.
    The basic idea is that the overloaded send() will read a wanted response
    based on the call from `return_values`.

    For changing values :func:`_set_state` will use :func:`pop()` to extract
     the first parameter and set the state accordingly.

    For a very simple device the following is enough, see :class:`TestPlug`
     for complete code.

    .. code-block::
        self.return_values = {
            "get_prop": self._get_state,
            "power": lambda x: self._set_state("power", x)
        }

    """

    def __init__(self, *args, **kwargs):
        self.start_state = self.state.copy()
        self._protocol = DummyMiIOProtocol(self)

    def _reset_state(self):
        """Revert back to the original state."""
        self.state = self.start_state.copy()

    def _set_state(self, var, value):
        """Set a state of a variable,
        the value is expected to be an array with length of 1."""
        # print("setting %s = %s" % (var, value))
        self.state[var] = value.pop(0)

    def _get_state(self, props):
        """Return wanted properties"""
        return [self.state[x] for x in props if x in self.state]


class DummyMiotDevice(DummyDevice):
    """Main class representing a MIoT device."""

    def __init__(self, *args, **kwargs):
        # {prop["did"]: prop["value"] for prop in self.miot_client.get_properties()}
        self.state = [{"did": k, "value": v, "code": 0} for k, v in self.state.items()]
        super().__init__(*args, **kwargs)

    def get_properties_for_mapping(self):
        return self.state

    def set_property(self, property_key: str, value):
        for prop in self.state:
            if prop["did"] == property_key:
                prop["value"] = value
        return None


class DummyMiotV2Device(DummyDevice):
    def __init__(self, *args, **kwargs):
        adapter = self.get_adapter()
        spec = adapter.spec

        def get_siid_and_piid(key: str):
            serv_name = key
            prop_name = key
            if "." in key:
                str_arr = key.split(".")
                serv_name = str_arr[0]
                prop_name = str_arr[1]
            serv, prop = spec.find_service_and_property(serv_name, prop_name)
            return {"siid": serv.iid, "piid": prop.iid}

        self.state = [
            {"did": k, "value": v, "code": 0, **get_siid_and_piid(k)}
            for k, v in self.state.items()
        ]
        super().__init__(*args, **kwargs)

    def get_readable_properties(self, request_props=None):
        return self.state

    def set_property(self, service_name: str, property_name: str, value):
        did = (
            service_name
            if service_name == property_name
            else service_name + "." + property_name
        )
        for prop in self.state:
            if prop["did"] == did:
                prop["value"] = value
        return None

    def get_adapter(self):
        pass
