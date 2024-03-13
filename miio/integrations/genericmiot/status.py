import logging
from typing import TYPE_CHECKING, Dict, Iterable

from miio import DeviceStatus
from miio.miot_models import DeviceModel, MiotAccess, MiotProperty

_LOGGER = logging.getLogger(__name__)


if TYPE_CHECKING:
    from .genericmiot import GenericMiot


class GenericMiotStatus(DeviceStatus):
    """Generic status for miot devices."""

    def __init__(self, response, dev):
        self._model: DeviceModel = dev._miot_model
        self._dev = dev
        self._data = {}
        self._data_by_siid_piid = {}
        self._data_by_normalized_name = {}
        self._initialize_data(response)

    def _initialize_data(self, response):
        def _is_valid_property_response(elem):
            code = elem.get("code")
            if code is None:
                _LOGGER.debug("Ignoring due to missing 'code': %s", elem)
                return False

            if code != 0:
                _LOGGER.warning("Ignoring due to error code '%s': %s", code, elem)
                return False

            needed_keys = ("did", "piid", "siid", "value")
            for key in needed_keys:
                if key not in elem:
                    _LOGGER.debug("Ignoring due to missing '%s': %s", key, elem)
                    return False

            return True

        for prop in response:
            if not _is_valid_property_response(prop):
                continue

            self._data[prop["did"]] = prop["value"]
            self._data_by_siid_piid[(prop["siid"], prop["piid"])] = prop["value"]
            self._data_by_normalized_name[self._normalize_name(prop["did"])] = prop[
                "value"
            ]

    @property
    def data(self):
        """Implemented to support json output."""
        return self._data

    def _normalize_name(self, id_: str) -> str:
        """Return a cleaned id for dict searches."""
        return id_.replace(":", "_").replace("-", "_")

    def __getattr__(self, item):
        """Return attribute for name.

        This is overridden to provide access to properties using (siid, piid) tuple.
        """
        # let devicestatus handle dunder methods
        if item.startswith("__") and item.endswith("__"):
            return super().__getattr__(item)

        normalized_name = self._normalize_name(item)
        if normalized_name in self._data_by_normalized_name:
            return self._data_by_normalized_name[normalized_name]

        # TODO: create a helper method and prohibit using non-normalized names
        if ":" in item:
            _LOGGER.warning("Use normalized names for accessing properties")
            serv, prop = item.split(":")
            prop = self._model.get_property(serv, prop)
            value = self._data[item]

            # TODO: this feels like a wrong place to convert value to enum..
            if prop.choices is not None:
                for choice in prop.choices:
                    if choice.value == value:
                        return choice.description

                _LOGGER.warning(
                    "Unable to find choice for value: %s: %s", value, prop.choices
                )

        return self._data[item]

    @property
    def device(self) -> "GenericMiot":
        """Return the device which returned this status."""
        return self._dev

    def property_dict(self) -> Dict[str, MiotProperty]:
        """Return name-keyed dictionary of properties."""
        res = {}

        # We use (siid, piid) to locate the property as not all devices mirror the did in response
        for (siid, piid), value in self._data_by_siid_piid.items():
            prop = self._model.get_property_by_siid_piid(siid, piid)
            prop.value = value
            res[prop.name] = prop

        return res

    @property
    def __cli_output__(self):
        """Return a CLI printable status."""
        out = ""
        props = self.property_dict()
        service = None
        for _name, prop in props.items():
            miot_prop: MiotProperty = prop.extras["miot_property"]
            if service is None or miot_prop.siid != service.siid:
                service = miot_prop.service
                out += f"Service [bold]{service.description} ({service.name})[/bold]\n"  # type: ignore  # FIXME

            out += f"\t{prop.description} ({prop.name}, access: {prop.pretty_access}): {prop.pretty_value}"

            if MiotAccess.Write in miot_prop.access:
                out += f" ({prop.format}"
                if prop.pretty_input_constraints is not None:
                    out += f", {prop.pretty_input_constraints}"
                out += ")"

            if self.device._debug > 1:
                out += "\n\t[bold]Extras[/bold]\n"
                for extra_key, extra_value in prop.extras.items():
                    out += f"\t\t{extra_key} = {extra_value}\n"

            out += "\n"

        return out

    def __dir__(self) -> Iterable[str]:
        """Return a list of properties."""
        return list(super().__dir__()) + list(self._data_by_normalized_name.keys())

    def __repr__(self):
        """Return string representation of the status."""
        s = f"<{self.__class__.__name__}"
        for name, value in self.property_dict().items():
            s += f" {name}={value}"
        s += ">"

        return s

    def __str__(self):
        """Return simplified string representation of the status."""
        s = f"<{self.__class__.__name__}"
        for name, value in self.property_dict().items():
            s += f" {name}={value.pretty_value}"
        s += ">"

        return s
