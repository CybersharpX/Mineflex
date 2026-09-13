"""Bot responding to chat commands like !pos, !health, !time, !quit."""

import asyncio

from mineflex import create_bot


async def main() -> None:
    bot = create_bot(
        host="localhost",
        port=25565,
        username="Commander",
        auth="offline",
    )

    @bot.on("chat")
    async def on_chat(username: str, message: str, *args):
        if username == bot.username or not message.startswith("!"):
            return

        cmd = message[1:].strip().lower()

        if cmd == "pos":
            pos = bot.position
            await bot.chat(f"My position is X: {pos.x:.1f}, Y: {pos.y:.1f}, Z: {pos.z:.1f}")
        elif cmd == "health":
            await bot.chat(f"Health: {bot.health:.1f}/20, Food: {bot.food}/20")
        elif cmd == "time":
            await bot.chat(f"Time of day: {bot.time_of_day}, Day: {bot.day}")
        elif cmd == "quit":
            await bot.chat("Goodbye!")
            await bot.quit()
        else:
            await bot.chat(f"Unknown command: !{cmd}. Available: !pos, !health, !time, !quit")

    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
