import asyncio
import json
import logging
import random
from collections import defaultdict
from typing import List, Union

import click

try:
    from pydantic.v1 import Field, validator
except ImportError:
    from pydantic import Field, validator
from miio import PushServer
from miio.miot_cloud import MiotCloud
from miio.miot_models import DeviceModel, MiotAccess, MiotProperty, MiotService

from .common import create_info_response, did_and_mac_for_model

_LOGGER = logging.getLogger(__name__)
UNSET = -10000

ERR_INVALID_SETTING = -1000


def create_random(values):
    """Create random value for the given mapping."""
    piid = values["piid"]
    if values["format"] == str:
        return f"piid {piid}"

    if values["choices"] is not None:
        choices = values["choices"]
        choice = choices[random.randint(0, len(choices) - 1)]  # nosec
        _LOGGER.debug("Got enum %r for %s", choice, piid)
        return choice.value

    if values["range"] is not None:
        range = values["range"]
        value = random.randint(range[0], range[1])  # nosec
        _LOGGER.debug("Got value %r from %s for piid %s", value, range, piid)
        return value

    if values["format"] == bool:
        value = bool(random.randint(0, 1))  # nosec
        _LOGGER.debug("Got bool %r for piid %s", value, piid)
        return value


class SimulatedMiotProperty(MiotProperty):
    """Simulates a property.

    * Creates dummy values based on the property information.
    * Validates inputs for set_properties
    """

    current_value: Union[int, str, bool] = Field(default=UNSET)

    @validator("current_value", pre=True, always=True)
    def verify_value(cls, v, values):
        """This verifies that the type of the value conforms with the mapping
        definition.

        This will also create random values for the mapping when the device is
        initialized.
        """
        if v == UNSET:
            return create_random(values)
        if MiotAccess.Write not in values["access"]:
            raise ValueError("Tried to set read-only property")

        try:
            casted_value = values["format"](v)
        except Exception as ex:
            raise TypeError("Invalid type") from ex

        range = values["range"]
        if range is not None and not (range[0] <= casted_value <= range[1]):
            raise ValueError(f"{casted_value} not in range {range}")

        choices = values["choices"]
        if choices is not None and not any(c.value == casted_value for c in choices):
            raise ValueError(f"{casted_value} not found in {choices}")

        return casted_value

    class Config:
        validate_assignment = True
        smart_union = True  # try all types before coercing


class SimulatedMiotService(MiotService):
    """Overridden to allow simulated properties."""

    properties: List[SimulatedMiotProperty] = Field(default=[], repr=False)


class SimulatedDeviceModel(DeviceModel):
    """Overridden to allow simulated properties."""

    services: List[SimulatedMiotService]


class MiotSimulator:
    """MiOT device simulator.

    This class implements a barebone simulator for a given devicemodel instance created
    from a miot schema file.
    """

    def __init__(self, device_model):
        self._model: SimulatedDeviceModel = device_model
        self._state = defaultdict(defaultdict)
        self.initialize_state()

    def initialize_state(self):
        """Create initial state for the device."""
        for serv in self._model.services:
            _LOGGER.debug("Found service: %s", serv)
            for act in serv.actions:
                _LOGGER.debug("Found action: %s", act)
            for prop in serv.properties:
                self._state[serv.siid][prop.piid] = prop
                _LOGGER.debug("Found property: %s", prop)

    def get_properties(self, payload):
        """Handle get_properties method."""
        _LOGGER.info("Got get_properties call with %s", payload)
        response = []
        params = payload["params"]
        for p in params:
            res = p.copy()
            try:
                res["value"] = self._state[res["siid"]][res["piid"]].current_value
                res["code"] = 0
            except Exception as ex:
                res["value"] = ""
                res["code"] = ERR_INVALID_SETTING
                res["exception"] = str(ex)
            response.append(res)

        return {"result": response}

    def set_properties(self, payload):
        """Handle set_properties method."""
        _LOGGER.info("Received set_properties call with %s", payload)
        params = payload["params"]
        for param in params:
            siid = param["siid"]
            piid = param["piid"]
            value = param["value"]
            self._state[siid][piid].current_value = value
            _LOGGER.info("Set %s:%s to %s", siid, piid, self._state[siid][piid])

        return {"result": 0}

    def dump_services(self, payload):
        """Dumps the available services."""
        servs = {}
        for serv in self._model.services:
            servs[serv.siid] = {"siid": serv.siid, "description": serv.description}

        return {"services": servs}

    def dump_properties(self, payload):
        """Dumps the available properties.

        This is not implemented on real devices, but can be used for debugging.
        """
        props = []
        params = payload["params"]
        if "siid" not in params:
            raise ValueError("missing 'siid'")

        siid = params["siid"]
        if siid not in self._state:
            raise ValueError(f"non-existing 'siid' {siid}")

        for piid, prop in self._state[siid].items():
            props.append(
                {
                    "siid": siid,
                    "piid": piid,
                    "prop": prop.description,
                    "value": prop.current_value,
                }
            )
        return {"result": props}

    def action(self, payload):
        """Handle action method."""
        params = payload["params"]
        if (
            "did" not in params
            or "siid" not in params
            or "aiid" not in params
            or "in" not in params
        ):
            raise ValueError("did, siid, or aiid missing")

        siid = params["siid"]
        aiid = params["aiid"]
        inputs = params["in"]
        service = self._model.get_service_by_siid(siid)

        action = service.get_action_by_id(aiid)
        action_inputs = action.inputs
        if len(inputs) != len(action_inputs):
            raise ValueError(
                "Invalid parameter count, was expecting %s params, got %s"
                % (len(inputs), len(action_inputs))
            )

        for idx, param in enumerate(inputs):
            wanted_input = action_inputs[idx]

            if wanted_input.choices:
                if not isinstance(param, int):
                    raise TypeError(
                        "Param #%s: enum value expects an integer %s, got %s"
                        % (idx, wanted_input, param)
                    )
                for choice in wanted_input.choices:
                    if param == choice.value:
                        break
                else:
                    raise ValueError(
                        "Param #%s: invalid value '%s' for %s"
                        % (idx, param, wanted_input.choices)
                    )

            elif wanted_input.range:
                if not isinstance(param, int):
                    raise TypeError(
                        "Param #%s: ranged value expects an integer %s, got %s"
                        % (idx, wanted_input, param)
                    )

                min, max, step = wanted_input.range
                if param < min or param > max:
                    raise ValueError(
                        "Param #%s: value '%s' out of range [%s, %s]"
                        % (idx, param, min, max)
                    )

            elif wanted_input.format == str and not isinstance(param, str):
                raise TypeError(f"Param #{idx}: expected string but got {type(param)}")

        _LOGGER.info("Got called %s", payload)
        return {"result": ["ok"]}


async def main(dev, model):
    device_id, mac = did_and_mac_for_model(model)
    server = PushServer(device_id=device_id)
    simulator = MiotSimulator(device_model=dev)
    server.add_method("miIO.info", create_info_response(model, "127.0.0.1", mac))
    server.add_method("action", simulator.action)
    server.add_method("get_properties", simulator.get_properties)
    server.add_method("set_properties", simulator.set_properties)
    server.add_method("dump_properties", simulator.dump_properties)
    server.add_method("dump_services", simulator.dump_services)

    transport, proto = await server.start()


@click.command()
@click.option("--file", type=click.File("r"), required=False)
@click.option("--model", type=str, required=True, default=None)
def miot_simulator(file, model):
    """Simulate miot device."""
    if file is not None:
        data = file.read()
        dev = SimulatedDeviceModel.parse_raw(data)
    else:
        cloud = MiotCloud()
        try:
            schema = cloud.get_model_schema(model)
        except Exception as ex:
            _LOGGER.error("Unable to get schema: %s" % ex)
            return
        try:
            dev = SimulatedDeviceModel.parse_obj(schema)
        except Exception as ex:
            # this is far from optimal, but considering this is a developer tool it can be fixed later
            fn = f"/tmp/pythonmiio_unparseable_{model}.json"  # nosec
            with open(fn, "w") as f:
                json.dump(schema, f, indent=4)
            _LOGGER.error("Unable to parse the schema, see %s: %s", fn, ex)
            return

    loop = asyncio.get_event_loop()
    random.seed(1)  # nosec
    loop.run_until_complete(main(dev, model=model))
    loop.run_forever()
