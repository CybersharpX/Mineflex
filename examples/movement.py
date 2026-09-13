"""Bot demonstrating movement controls (walking, sprinting, jumping, looking)."""

import asyncio

from mineflex import create_bot


async def main() -> None:
    bot = create_bot(
        host="localhost",
        port=25565,
        username="Walker",
        auth="offline",
        physics_enabled=True,
    )

    @bot.on("chat")
    async def on_chat(username: str, message: str, *args):
        if message == "!jump":
            await bot.chat("Jumping!")
            bot.set_control_state("jump", True)
            await asyncio.sleep(0.2)
            bot.set_control_state("jump", False)

        elif message == "!walk":
            await bot.chat("Walking forward for 2 seconds...")
            bot.set_control_state("forward", True)
            await asyncio.sleep(2.0)
            bot.set_control_state("forward", False)
            await bot.chat("Stopped walking.")

        elif message == "!sprint":
            await bot.chat("Sprinting forward for 2 seconds...")
            bot.set_control_state("sprint", True)
            bot.set_control_state("forward", True)
            await asyncio.sleep(2.0)
            bot.clear_control_states()
            await bot.chat("Stopped sprinting.")

    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
