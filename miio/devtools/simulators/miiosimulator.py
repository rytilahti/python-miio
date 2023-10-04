"""Implementation of miio simulator."""
import asyncio
import json
import logging
from typing import List, Optional, Union

import click

try:
    from pydantic.v1 import BaseModel, Field, PrivateAttr
except ImportError:
    from pydantic import BaseModel, Field, PrivateAttr
from yaml import safe_load

from miio import PushServer

from .common import create_info_response, did_and_mac_for_model

_LOGGER = logging.getLogger(__name__)


class Format(type):
    @classmethod
    def __get_validators__(cls):
        yield cls.convert_type

    @classmethod
    def convert_type(cls, input: str):
        type_map = {
            "bool": bool,
            "int": int,
            "str_bool": str,
            "str": str,
            "float": float,
        }
        return type_map[input]


class MiioProperty(BaseModel):
    """Single miio property."""

    name: str
    type: Format
    value: Optional[Union[str, bool, int]]
    models: List[str] = Field(default=[])
    setter: Optional[str] = None
    description: Optional[str] = None
    min: Optional[int] = None
    max: Optional[int] = None

    class Config:
        extra = "forbid"


class MiioAction(BaseModel):
    """Simulated miio action."""


class MiioMethod(BaseModel):
    """Simulated method."""

    name: str
    result: Optional[List] = None
    result_json: Optional[str] = None


class MiioModel(BaseModel):
    """Model information."""

    model: str
    name: Optional[str] = "unknown name"


class SimulatedMiio(BaseModel):
    """Simulated device model for miio devices."""

    name: Optional[str] = Field(default="Unnamed integration")
    models: List[MiioModel]
    type: str
    properties: List[MiioProperty] = Field(default=[])
    actions: List[MiioAction] = Field(default=[])
    methods: List[MiioMethod] = Field(default=[])
    _model: Optional[str] = PrivateAttr(default=None)

    class Config:
        extra = "forbid"


class MiioSimulator:
    """Simple miio device simulator."""

    def __init__(self, dev: SimulatedMiio, server: PushServer):
        self._dev = dev
        self._setters = {}
        self._server = server

        # Add get_prop if device has properties defined
        if self._dev.properties:
            server.add_method("get_prop", self.get_prop)
        # initialize setters
        for prop in self._dev.properties:
            if prop.models and self._dev._model not in prop.models:
                continue
            if prop.setter is not None:
                self._setters[prop.setter] = prop
                server.add_method(prop.setter, self.handle_set)

        # Add static methods
        for method in self._dev.methods:
            if method.result_json:
                server.add_method(
                    method.name, {"result": json.loads(method.result_json)}
                )
            else:
                server.add_method(method.name, {"result": method.result})

    def get_prop(self, payload):
        """Handle get_prop."""
        params = payload["params"]

        resp = []
        current_state = {prop.name: prop for prop in self._dev.properties}
        for param in params:
            p = current_state[param]
            resp.append(p.type(p.value))

        return {"result": resp}

    def handle_set(self, payload):
        """Handle setter methods."""
        _LOGGER.info("Got setter call with %s", payload)
        self._setters[payload["method"]].value = payload["params"][0]

        return {"result": ["ok"]}


async def main(dev):
    if dev._model is None:
        dev._model = next(iter(dev.models)).model
        _LOGGER.warning(
            "No --model defined, using the first supported one: %s", dev._model
        )

    did, mac = did_and_mac_for_model(dev._model)
    server = PushServer(device_id=did)

    _ = MiioSimulator(dev=dev, server=server)
    server.add_method("miIO.info", create_info_response(dev._model, "127.0.0.1", mac))

    await server.start()


@click.command()
@click.option("--file", type=click.File("r"), required=True)
@click.option("--model", type=str, required=False)
def miio_simulator(file, model):
    """Simulate miio device."""
    data = file.read()
    dev = SimulatedMiio.parse_obj(safe_load(data))
    _LOGGER.info("Available models: %s", dev.models)
    if model is not None:
        dev._model = model
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(dev))
    loop.run_forever()
