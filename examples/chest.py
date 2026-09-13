"""Bot interacting with chests and container windows."""

import asyncio

from mineflex import create_bot


async def main() -> None:
    bot = create_bot(
        host="localhost",
        port=25565,
        username="ChestBot",
        auth="offline",
    )

    @bot.on("window_open")
    async def on_window_open(window):
        print(f"Window opened: {window.title} (ID: {window.id}, Slots: {len(window.slots)})")
        await bot.chat(f"Opened {window.title}!")

    @bot.on("window_close")
    async def on_window_close(window):
        print(f"Window closed: {window.title}")

    @bot.on("chat")
    async def on_chat(username: str, message: str, *args):
        if message == "!open":
            chest_block = bot.find_block("chest", max_distance=4)
            if not chest_block:
                await bot.chat("No chest within reach.")
                return

            # Activate chest block to request open screen packet
            await bot.client.send_packet(
                # UseItemOn block packet to open
                bot.building_manager.place_block(chest_block, face_vector=chest_block.position)  # type: ignore
            )

    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
