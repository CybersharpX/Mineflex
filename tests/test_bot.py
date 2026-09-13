"""Unit tests for Bot initialization, plugins, and lifecycle."""

from mineflex import Bot, create_bot
from mineflex.plugins.base import Plugin


class SamplePlugin(Plugin):
    name = "sample_plugin"

    def setup(self, bot: Bot) -> None:
        bot.custom_plugin_loaded = True


def sample_callable_plugin(bot: Bot) -> None:
    bot.callable_plugin_loaded = True


def test_create_bot_defaults():
    bot = create_bot(
        host="mc.example.com",
        port=25565,
        username="TestBot",
        auth="offline",
    )
    assert bot.host == "mc.example.com"
    assert bot.port == 25565
    assert bot.username == "TestBot"
    assert bot.auth_mode == "offline"
    assert bot.physics_enabled is True


def test_plugin_loading():
    bot = create_bot(username="PluginBot")
    bot.load_plugin(SamplePlugin())
    bot.load_plugin(sample_callable_plugin)

    assert getattr(bot, "custom_plugin_loaded", False) is True
    assert getattr(bot, "callable_plugin_loaded", False) is True
