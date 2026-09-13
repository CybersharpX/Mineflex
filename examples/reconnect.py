"""Bot illustrating clean reconnect with exponential backoff on disconnect."""

import asyncio

from mineflex import create_bot


async def connect_with_retry(max_attempts: int = 5) -> None:
    attempt = 0
    delay = 2.0

    while attempt < max_attempts:
        attempt += 1
        print(f"Connecting attempt {attempt}/{max_attempts}...")

        bot = create_bot(
            host="localhost",
            port=25565,
            username="PersistentBot",
            auth="offline",
        )

        @bot.on("spawn")
        async def on_spawn():
            print("Bot joined and spawned!")

        @bot.on("kicked")
        async def on_kicked(reason):
            print(f"Bot was kicked: {reason}")

        try:
            await bot.run()
        except Exception as exc:
            print(f"Connection ended with error: {exc}")

        print(f"Connection closed. Waiting {delay:.1f}s before reconnecting...")
        await asyncio.sleep(delay)
        delay = min(delay * 1.5, 30.0)


if __name__ == "__main__":
    asyncio.run(connect_with_retry())
