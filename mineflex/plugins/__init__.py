"""Plugin architecture and internal plugins for Mineflex."""

from __future__ import annotations

from mineflex.plugins.base import Plugin, PluginManager
from mineflex.plugins.internal import STANDARD_INTERNAL_PLUGINS

__all__ = ["Plugin", "PluginManager", "STANDARD_INTERNAL_PLUGINS"]
