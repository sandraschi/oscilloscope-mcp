"""Portmanteau tools for oscilloscope-mcp."""

from .capture import scope_capture
from .configure import scope_configure
from .device import scope_device
from .help import scope_help
from .measure import scope_measure
from .trigger import scope_trigger

__all__ = [
    "scope_capture",
    "scope_configure",
    "scope_device",
    "scope_help",
    "scope_measure",
    "scope_trigger",
]
