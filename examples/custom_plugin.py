"""Demonstration of writing and loading custom plugins in Mineflex."""

import asyncio

from mineflex import Bot, create_bot
from mineflex.plugins import Plugin


class AutoGreetPlugin(Plugin):
    """Custom plugin that welcomes newly joined players."""

    name = "auto_greet"

    def setup(self, bot: Bot) -> None:
        @bot.on("entity_spawn")
        async def on_entity_spawn(entity):
            # If a player spawned nearby that isn't the bot itself
            if entity.name == "player" and entity.id != bot.entity.id:
                print(f"[Plugin] Detected nearby player entity ID {entity.id}!")
                await bot.chat("Welcome to the server, friend!")


async def main() -> None:
    bot = create_bot(
        host="localhost",
        port=25565,
        username="Greeter",
        auth="offline",
    )

    # Load custom plugin
    bot.load_plugin(AutoGreetPlugin())

    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
