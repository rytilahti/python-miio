from typing import Dict, cast

from miio.descriptors import ActionDescriptor, PropertyDescriptor
from miio.miot_models import MiotProperty, MiotService

# TODO: these should be moved to a generic implementation covering all actions and settings


def pretty_actions(result: Dict[str, ActionDescriptor]):
    """Pretty print actions."""
    out = ""
    service = None
    for _, desc in result.items():
        miot_prop: MiotProperty = desc.extras["miot_action"]
        # service is marked as optional due pydantic backrefs..
        serv = cast(MiotService, miot_prop.service)
        if service is None or service.siid != serv.siid:
            service = serv
            out += f"[bold]{service.description} ({service.name})[/bold]\n"

        out += f"\t{desc.id}\t\t{desc.name}"
        if desc.inputs:
            for idx, input_ in enumerate(desc.inputs, start=1):
                param = input_.extras[
                    "miot_property"
                ]  # TODO: hack until descriptors get support for descriptions
                param_desc = f"\n\t\tParameter #{idx}: {param.name} ({param.description}) ({param.format}) {param.pretty_input_constraints}"
                out += param_desc

        out += "\n"

    return out


def pretty_properties(result: Dict[str, PropertyDescriptor]):
    """Pretty print settings."""
    out = ""
    verbose = False
    service = None
    for _, desc in result.items():
        miot_prop: MiotProperty = desc.extras["miot_property"]
        # service is marked as optional due pydantic backrefs..
        serv = cast(MiotService, miot_prop.service)
        if service is None or service.siid != serv.siid:
            service = serv
            out += f"[bold]{service.name}[/bold] ({service.description})\n"

        out += f"\t{desc.name} ({desc.id}, access: {miot_prop.pretty_access})\n"
        if verbose:
            out += f'  urn: {repr(desc.extras["urn"])}\n'
            out += f'  siid: {desc.extras["siid"]}\n'
            out += f'  piid: {desc.extras["piid"]}\n'

    return out
