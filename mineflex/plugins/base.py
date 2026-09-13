"""Plugin system base classes and manager."""

from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any, Callable, List, Union

from mineflex.logging import get_logger

if TYPE_CHECKING:
    pass

logger = get_logger("mineflex.plugins")


class Plugin:
    """Base class for object-oriented Mineflex plugins."""

    name: str = "plugin"

    def setup(self, bot: Any) -> Any:
        """Called when the plugin is loaded into the bot."""
        pass


PluginType = Union[Plugin, Callable[[Any], Any]]


class PluginManager:
    """Manages bot plugins and extensions."""

    def __init__(self, bot: Any) -> None:
        self.bot = bot
        self._plugins: List[PluginType] = []

    def load_plugin(self, plugin: PluginType) -> None:
        """Load a plugin instance or callable function into the bot."""
        if plugin in self._plugins:
            return

        self._plugins.append(plugin)
        try:
            if isinstance(plugin, Plugin):
                res = plugin.setup(self.bot)
                if inspect.isawaitable(res):
                    try:
                        import asyncio

                        asyncio.ensure_future(res)
                    except RuntimeError:
                        pass
            elif callable(plugin):
                res = plugin(self.bot)
                if inspect.isawaitable(res):
                    try:
                        import asyncio

                        asyncio.ensure_future(res)
                    except RuntimeError:
                        pass
            logger.info("Loaded plugin: %s", getattr(plugin, "name", repr(plugin)))
        except Exception as exc:
            logger.error("Failed to setup plugin %s: %s", plugin, exc, exc_info=True)

    def load_plugins(self, plugins: List[PluginType]) -> None:
        for p in plugins:
            self.load_plugin(p)

    def has_plugin(self, plugin: PluginType) -> bool:
        return plugin in self._plugins
