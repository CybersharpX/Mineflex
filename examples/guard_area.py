"""Bot that guards a perimeter against hostile mobs."""

import asyncio

from mineflex import create_bot
from mineflex.types import Vec3


async def main() -> None:
    bot = create_bot(
        host="localhost",
        port=25565,
        username="Sentinel",
        auth="offline",
    )

    guard_center: Vec3 | None = None
    guard_radius = 12.0

    @bot.on("spawn")
    async def on_spawn():
        nonlocal guard_center
        guard_center = bot.position.clone()
        print(f"Guarding perimeter at {guard_center.floored()} (radius: {guard_radius}m)")

    @bot.on("physics_tick")
    async def on_tick():
        if not guard_center:
            return

        # Find closest hostile mob within guard perimeter
        target = bot.nearest_entity(
            lambda e: (
                e.category == "hostile" and e.position.distance_to(guard_center) <= guard_radius
            ),
            max_distance=guard_radius,
        )

        if target:
            dist = bot.position.distance_to(target.position)
            await bot.look_at(target.eye_position)
            if dist <= 3.5:
                await bot.attack(target)

    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
