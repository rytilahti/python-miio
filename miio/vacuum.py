"""This file is just for compat reasons and prints out a deprecated warning when
executed."""
import warnings

from .integrations.vacuum.roborock.vacuum import *  # noqa: F403,F401

warnings.warn(
    "miio.vacuum module has been renamed to miio.integrations.vacuum.roborock.vacuum",
    DeprecationWarning,
)
