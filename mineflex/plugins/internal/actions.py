"""Internal plugin binding digging, placing, combat, and vehicle actions to bot."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mineflex.actions.building import BuildingManager
from mineflex.actions.combat import CombatManager
from mineflex.actions.digging import DiggingManager
from mineflex.actions.vehicles import VehicleManager
from mineflex.entity.entity import Entity
from mineflex.types import Vec3
from mineflex.world.block import Block

if TYPE_CHECKING:
    from mineflex.bot import Bot


def inject_actions(bot: Bot) -> None:
    """Inject digging, building, combat, and vehicle actions into the bot."""
    bot.digging_manager = DiggingManager(bot)
    bot.building_manager = BuildingManager(bot)
    bot.combat_manager = CombatManager(bot)
    bot.vehicle_manager = VehicleManager(bot)

    async def dig(block: Block, force_look: bool = True) -> None:
        await bot.digging_manager.dig(block, force_look=force_look)

    async def stop_digging() -> None:
        await bot.digging_manager.stop_digging()

    async def place_block(reference_block: Block, face_vector: Vec3) -> None:
        await bot.building_manager.place_block(reference_block, face_vector)

    async def attack(entity: Entity, swing: bool = True) -> None:
        await bot.combat_manager.attack(entity, swing=swing)

    async def mount(entity: Entity) -> None:
        await bot.vehicle_manager.mount(entity)

    async def dismount() -> None:
        await bot.vehicle_manager.dismount()

    bot.dig = dig  # type: ignore
    bot.stop_digging = stop_digging  # type: ignore
    bot.place_block = place_block  # type: ignore
    bot.attack = attack  # type: ignore
    bot.mount = mount  # type: ignore
    bot.dismount = dismount  # type: ignore
