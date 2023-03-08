import logging
from typing import Dict, List, Optional, Type

import click

from .device import Device
from .exceptions import DeviceException

_LOGGER = logging.getLogger(__name__)


class DeviceFactory:
    """A helper class to construct devices based on their info responses.

    This class keeps list of supported integrations and models to allow creating
    :class:`Device` instances without knowing anything except the host and the token.

    :func:`create` is the main entry point when using this module. Example::

        from miio import DeviceFactory

        dev = DeviceFactory.create("127.0.0.1", 32*"0")
    """

    _integration_classes: List[Type[Device]] = []
    _supported_models: Dict[str, Type[Device]] = {}

    @classmethod
    def register(cls, integration_cls: Type[Device]):
        """Register class for to the registry."""
        cls._integration_classes.append(integration_cls)
        _LOGGER.debug("Registering %s", integration_cls.__name__)
        for model in integration_cls.supported_models:  # type: ignore
            if model in cls._supported_models:
                _LOGGER.debug(
                    "Ignoring duplicate of %s for %s, previously registered by %s",
                    model,
                    integration_cls,
                    cls._supported_models[model],
                )
                continue

            _LOGGER.debug("  * %s => %s", model, integration_cls)
            cls._supported_models[model] = integration_cls

    @classmethod
    def supported_models(cls) -> Dict[str, Type[Device]]:
        """Return a dictionary of models and their corresponding implementation
        classes."""
        return cls._supported_models

    @classmethod
    def integrations(cls) -> List[Type[Device]]:
        """Return the list of integration classes."""
        return cls._integration_classes

    @classmethod
    def class_for_model(cls, model: str):
        """Return implementation class for the given model, if available."""
        if model in cls._supported_models:
            return cls._supported_models[model]

        wildcard_models = {
            m: impl for m, impl in cls._supported_models.items() if m.endswith("*")
        }
        # We sort here to return the implementation with most specific prefix
        sorted_by_longest_prefix = sorted(
            wildcard_models.items(), key=lambda item: len(item[0]), reverse=True
        )
        for wildcard_model, impl in sorted_by_longest_prefix:
            m = wildcard_model.rstrip("*")
            if model.startswith(m):
                _LOGGER.debug(
                    "Using %s for %s, please add it to supported models for %s",
                    wildcard_model,
                    model,
                    impl,
                )
                return impl

        raise DeviceException("No implementation found for model %s" % model)

    @classmethod
    def create(
        self,
        host: str,
        token: str,
        model: Optional[str] = None,
        *,
        force_generic_miot=False,
    ) -> Device:
        """Return instance for the given host and token, with optional model override.

        The optional model parameter can be used to override the model detection.
        """
        dev: Device
        if force_generic_miot:  # TODO: find a better way to handle this.
            from .integrations.genericmiot.genericmiot import GenericMiot

            dev = GenericMiot(host, token, model=model)
            dev.info()
            return dev
        if model is None:
            dev = Device(host, token)
            info = dev.info()
            model = info.model

        return self.class_for_model(model)(host, token, model=model)


@click.group()
def factory():
    """Access to available integrations."""


@factory.command()
def integrations():
    for integration in DeviceFactory.integrations():
        click.echo(
            f"* {integration} supports {len(integration.supported_models)} models"
        )


@factory.command()
def models():
    """List supported models."""
    for model in DeviceFactory.supported_models():
        click.echo(f"* {model}")
