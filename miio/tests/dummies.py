class DummyMiIOProtocol:
    """DummyProtocol allows you mock MiIOProtocol."""

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
        self._info = None
        # TODO: ugly hack to check for pre-existing _model
        if getattr(self, "_model", None) is None:
            self._model = "dummy.model"
        self.token = "ffffffffffffffffffffffffffffffff"  # nosec
        self.ip = "192.0.2.1"

    def _reset_state(self):
        """Revert back to the original state."""
        self.state = self.start_state.copy()

    def _set_state(self, var, value):
        """Set a state of a variable, the value is expected to be an array with length
        of 1."""
        # print("setting %s = %s" % (var, value))
        self.state[var] = value.pop(0)

    def _get_state(self, props):
        """Return wanted properties."""
        return [self.state[x] for x in props if x in self.state]


class DummyMiotDevice(DummyDevice):
    """Main class representing a MIoT device."""

    def __init__(self, *args, **kwargs):
        # {prop["did"]: prop["value"] for prop in self.miot_client.get_properties()}
        self.state = [{"did": k, "value": v, "code": 0} for k, v in self.state.items()]
        super().__init__(*args, **kwargs)

    def get_properties_for_mapping(self, *, max_properties=15):
        return self.state

    def get_properties(
        self, properties, *, property_getter="get_prop", max_properties=None
    ):
        """Return values only for listed properties."""
        keys = [p["did"] for p in properties]
        props = []
        for prop in self.state:
            if prop["did"] in keys:
                props.append(prop)

        return props

    def set_property(self, property_key: str, value):
        for prop in self.state:
            if prop["did"] == property_key:
                prop["value"] = value
        return None
