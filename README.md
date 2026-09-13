# Mineflex

[![Python Tests](https://github.com/mineflex/mineflex/actions/workflows/ci.yml/badge.svg)](https://github.com/mineflex/mineflex/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

**Mineflex** is a production-quality, native Python Minecraft bot framework inspired by and behaviorally compatible with PrismarineJS's [Mineflayer](https://github.com/PrismarineJS/mineflayer).

It is written **100% in native Python** using modern `asyncio`, dataclasses, type hints, and structured event dispatching. It does not use any Node.js runtime, subprocess wrappers, or RPC bridges.

---

## Minimal Example

```python
import asyncio
from mineflex import create_bot


async def main():
    bot = create_bot(
        host="localhost",
        port=25565,
        username="PythonBot",
        auth="offline",
    )

    @bot.on("spawn")
    async def on_spawn():
        print(f"Spawned at {bot.position}!")
        await bot.chat("Hello from native Python!")

    @bot.on("chat")
    async def on_chat(username, message, *args):
        if username != bot.username:
            if message == "!ping":
                await bot.chat("pong!")

    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Architectural Highlights

* **Asyncio-Native Architecture**: Clean separation between awaitable network commands (`bot.chat()`, `bot.dig()`, `bot.place_block()`, `bot.attack()`) and synchronous instant state queries (`bot.position`, `bot.health`, `bot.inventory`, `bot.block_at()`).
* **Deterministic 20 Hz Physics Engine**: Independent physics engine with exact Minecraft constants for gravity (-0.08), air drag (0.98), ground friction (0.6 * 0.91), jumping (+0.42), sprinting, sneaking, auto-stepping over 0.6 block height obstacles, and AABB collision resolution.
* **Paletted Chunks & World State**: Full 1.20+ chunk section paletted bit array decoding (single-value, indirect palette, and direct palette) with fast spatial lookups (`find_blocks`, `find_block`).
* **Server-Authoritative Inventory**: Complete 46-slot player inventory model and container window abstractions (chests, furnaces, crafting tables) supporting slot click transactions.
* **Rich Chat & Component Trees**: Parses vanilla JSON chat component trees, translation templates, color formatting, and legacy `§` section formatting.
* **Modular Internal Plugins**: Functionality is structured into modular internal plugins (`chat`, `health`, `game`, `time`, `blocks`, `entities`, `physics`, `inventory`, `actions`), keeping `Bot` clean and maintainable.
* **Extensible Custom Plugins**: Supports both class-based `Plugin` and callable function plugins.

---

## Documentation

* [Getting Started](docs/getting_started.md)
* [Architecture Guide](docs/architecture.md)
* [API Reference](docs/api.md)
* [Protocol Codecs & Framing](docs/protocol.md)
* [Physics Simulation](docs/physics.md)
* [Plugin System](docs/plugins.md)
* [Authentication](docs/authentication.md)
* [Compatibility Matrix](docs/compatibility_matrix.md)
* [Migration from Mineflayer](docs/migration_from_mineflayer.md)
* [Troubleshooting](docs/troubleshooting.md)

---

## Running Tests

Run the complete test suite including unit tests and end-to-end mock server integration tests:

```bash
python -m pytest
```

---

## License

This project is licensed under the [MIT License](LICENSE).
