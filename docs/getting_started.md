# Getting Started with Mineflex

Mineflex is an asynchronous, event-driven, production-quality Python framework for building Minecraft bots, behaviorally compatible with PrismarineJS's Mineflayer.

---

## Installation

Mineflex requires Python 3.10+ and uses modern packaging standards.

```bash
# Standard installation
pip install mineflex

# Development installation with test and lint tooling
pip install -e ".[dev]"
```

---

## Quickstart

Create a file named `bot.py`:

```python
import asyncio
from mineflex import create_bot


async def main():
    # 1. Initialize bot configuration
    bot = create_bot(
        host="localhost",
        port=25565,
        username="PythonBot",
        auth="offline",
        version="1.20.1",
    )

    # 2. Register lifecycle and gameplay event handlers
    @bot.on("spawn")
    async def on_spawn():
        print(f"Bot spawned at position: {bot.position}")
        await bot.chat("Hello from Mineflex!")

    @bot.on("chat")
    async def on_chat(username, message, *args):
        # Prevent responding to our own messages
        if username == bot.username:
            return

        print(f"[{username}] {message}")
        if message == "!ping":
            await bot.chat("pong!")

    # 3. Start bot event loop
    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
```

Run the bot:

```bash
python bot.py
```

---

## Key Features

* **Asyncio-Native**: Pure Python asynchronous event loop architecture. Network operations (`chat`, `dig`, `place_block`, `attack`) are awaitable, while state queries (`position`, `health`, `inventory`, `block_at`) are instant and synchronous.
* **Independent Physics Engine**: Standalone 20 Hz simulation supporting gravity, ground friction, air drag, jumping, sprinting, sneaking, stepping over obstacles, and AABB block collision.
* **Full Paletted World State**: Fast 1.20.x chunk column parsing, section palettes, and spatial queries.
* **Server-Authoritative Inventory**: Complete slots, container windows (chests, crafting tables, furnaces), and item equipment tracking.
* **Rich Chat Parsing**: Automatic decoding of vanilla JSON component trees, translations, colors, and legacy section formatting.
