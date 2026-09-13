"""Bot that finds and digs a specific block type on command."""

import asyncio

from mineflex import create_bot


async def main() -> None:
    bot = create_bot(
        host="localhost",
        port=25565,
        username="Miner",
        auth="offline",
    )

    @bot.on("chat")
    async def on_chat(username: str, message: str, *args):
        if message.startswith("!dig "):
            block_name = message.split(" ", 1)[1].strip().lower()
            target = bot.find_block(block_name, max_distance=4)

            if not target:
                await bot.chat(f"No {block_name} found within reach (4 blocks).")
                return

            await bot.chat(f"Starting to dig {target.name} at {target.position.floored()}...")
            try:
                await bot.dig(target)
                await bot.chat(f"Finished digging {target.name}!")
            except Exception as exc:
                await bot.chat(f"Failed to dig: {exc}")

    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
