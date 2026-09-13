"""Bot that looks at and follows a specified player."""

import asyncio

from mineflex import create_bot


async def main() -> None:
    bot = create_bot(
        host="localhost",
        port=25565,
        username="Follower",
        auth="offline",
        physics_enabled=True,
    )

    following_player = None

    @bot.on("chat")
    async def on_chat(username: str, message: str, *args):
        nonlocal following_player
        if message == "!follow":
            player = bot.players.get(username)
            if player and player.entity:
                following_player = player.username
                await bot.chat(f"Following {username}!")
            else:
                await bot.chat(f"Cannot see you in visual range, {username}.")
        elif message == "!stop":
            following_player = None
            bot.clear_control_states()
            await bot.chat("Stopped following.")

    @bot.on("physics_tick")
    async def on_physics_tick():
        nonlocal following_player
        if not following_player:
            return

        player = bot.players.get(following_player)
        if not player or not player.entity:
            return

        target_pos = player.entity.position
        dist = bot.position.distance_to(target_pos)

        # Look towards player
        await bot.look_at(player.entity.eye_position)

        if dist > 3.0:
            bot.set_control_state("forward", True)
            if dist > 8.0:
                bot.set_control_state("sprint", True)
            else:
                bot.set_control_state("sprint", False)
        else:
            bot.set_control_state("forward", False)
            bot.set_control_state("sprint", False)

    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
