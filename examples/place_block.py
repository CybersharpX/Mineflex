"""Bot that places a block below its feet or against an adjacent block."""

import asyncio

from mineflex import create_bot
from mineflex.types import Vec3


async def main() -> None:
    bot = create_bot(
        host="localhost",
        port=25565,
        username="Builder",
        auth="offline",
    )

    @bot.on("chat")
    async def on_chat(username: str, message: str, *args):
        if message == "!place":
            # Find block directly beneath the bot
            ref_pos = bot.position.offset(0, -1, 0)
            ref_block = bot.block_at(ref_pos)

            if ref_block.is_air:
                await bot.chat("No reference block underneath me.")
                return

            try:
                # Place block on the top face (+Y) of the reference block
                await bot.place_block(ref_block, face_vector=Vec3(0, 1, 0))
                await bot.chat("Block placed successfully!")
            except Exception as exc:
                await bot.chat(f"Failed to place block: {exc}")

    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
