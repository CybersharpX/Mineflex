"""Bot that locates specific block types in the surrounding world."""

import asyncio

from mineflex import create_bot


async def main() -> None:
    bot = create_bot(
        host="localhost",
        port=25565,
        username="Prospector",
        auth="offline",
    )

    @bot.on("chat")
    async def on_chat(username: str, message: str, *args):
        if message.startswith("!find "):
            block_name = message.split(" ", 1)[1].strip().lower()
            await bot.chat(f"Searching for {block_name} within 32 blocks...")

            closest = bot.find_block(block_name, max_distance=32)
            if closest:
                dist = bot.position.distance_to(closest.position)
                await bot.chat(
                    f"Found {block_name} at {closest.position.floored()} ({dist:.1f} blocks away)."
                )
            else:
                await bot.chat(f"Could not find any {block_name} nearby.")

    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
