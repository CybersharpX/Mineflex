"""Bot attacking hostile mobs or specified targets."""

import asyncio

from mineflex import create_bot


async def main() -> None:
    bot = create_bot(
        host="localhost",
        port=25565,
        username="Warrior",
        auth="offline",
    )

    @bot.on("chat")
    async def on_chat(username: str, message: str, *args):
        if message == "!attack":
            # Target nearest hostile mob
            target = bot.nearest_entity(lambda e: e.category == "hostile", max_distance=4.0)

            if not target:
                await bot.chat("No hostile mobs within attack reach (4.0 blocks).")
                return

            await bot.chat(f"Attacking {target.name} (ID: {target.id})!")
            await bot.look_at(target.eye_position)
            await bot.attack(target)

    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
