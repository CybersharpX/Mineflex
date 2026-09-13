"""Bot that inspects players in the tablist or world and reports details."""

import asyncio

from mineflex import create_bot


async def main() -> None:
    bot = create_bot(
        host="localhost",
        port=25565,
        username="Inspector",
        auth="offline",
    )

    @bot.on("chat")
    async def on_chat(username: str, message: str, *args):
        if message.startswith("!inspect "):
            target_name = message.split(" ", 1)[1].strip()
            player = bot.players.get(target_name)

            if not player:
                await bot.chat(f"Player '{target_name}' is not in tablist.")
                return

            info = f"Player {player.username} (ping: {player.ping}ms, gamemode: {player.gamemode})"
            if player.entity:
                pos = player.entity.position
                dist = bot.position.distance_to(pos)
                info += f" at ({pos.x:.1f}, {pos.y:.1f}, {pos.z:.1f}), distance: {dist:.1f} blocks."
            else:
                info += " (out of visual range)."

            await bot.chat(info)

    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
