"""Bot tracking nearby entities and reporting lifecycle events."""

import asyncio

from mineflex import create_bot


async def main() -> None:
    bot = create_bot(
        host="localhost",
        port=25565,
        username="Tracker",
        auth="offline",
    )

    @bot.on("entity_spawn")
    async def on_entity_spawn(entity):
        print(f"[SPAWN] {entity.name} (ID: {entity.id}) at {entity.position.floored()}")

    @bot.on("entity_gone")
    async def on_entity_gone(entity):
        print(f"[DESPAWN] {entity.name} (ID: {entity.id}) left the world.")

    @bot.on("chat")
    async def on_chat(username: str, message: str, *args):
        if message == "!nearby":
            entities = list(bot.entities.values())
            summary = [
                f"{e.name} (dist {bot.position.distance_to(e.position):.1f}m)" for e in entities[:5]
            ]
            if summary:
                await bot.chat("Nearby: " + ", ".join(summary))
            else:
                await bot.chat("No entities detected nearby.")

    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
