"""Minimal hello world bot in Mineflex."""

import asyncio

from mineflex import create_bot


async def main() -> None:
    bot = create_bot(
        host="localhost",
        port=25565,
        username="HelloBot",
        auth="offline",
    )

    @bot.on("spawn")
    async def on_spawn():
        print(f"Bot successfully spawned in world at {bot.position}!")
        await bot.chat("Hello, Minecraft world from Mineflex!")

    @bot.on("error")
    def on_error(err):
        print(f"Encountered error: {err}")

    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
