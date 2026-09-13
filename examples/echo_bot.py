"""Echo bot replying to public player messages."""

import asyncio

from mineflex import create_bot


async def main() -> None:
    bot = create_bot(
        host="localhost",
        port=25565,
        username="EchoBot",
        auth="offline",
    )

    @bot.on("spawn")
    async def on_spawn():
        print("EchoBot ready. Listening for chat...")

    @bot.on("chat")
    async def on_chat(username: str, message: str, *args):
        # Ignore our own messages
        if username == bot.username:
            return

        print(f"[{username}] {message}")
        await bot.chat(f"You said: {message}")

    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
