"""Internal plugin for entity tracking and tablist players."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Optional

from mineflex.entity.entity import Entity
from mineflex.entity.tracker import EntityTracker
from mineflex.protocol.packets.play.entities import (
    DestroyEntitiesPacket,
    SetEntityVelocityPacket,
    SpawnEntityPacket,
    UpdateEntityPositionPacket,
    UpdateEntityPositionRotationPacket,
    UpdateEntityRotationPacket,
)

if TYPE_CHECKING:
    from mineflex.bot import Bot


def inject_entities(bot: Bot) -> None:
    """Inject entity tracking and nearest entity queries into bot."""
    bot.entity_tracker = EntityTracker(registry=bot.registry, emitter=bot)

    bot.client.register_handler(SpawnEntityPacket, bot.entity_tracker.spawn_entity)
    bot.client.register_handler(UpdateEntityPositionPacket, bot.entity_tracker.update_position)
    bot.client.register_handler(
        UpdateEntityPositionRotationPacket, bot.entity_tracker.update_position_rotation
    )
    bot.client.register_handler(UpdateEntityRotationPacket, bot.entity_tracker.update_rotation)
    bot.client.register_handler(SetEntityVelocityPacket, bot.entity_tracker.update_velocity)
    bot.client.register_handler(DestroyEntitiesPacket, bot.entity_tracker.destroy_entities)

    def nearest_entity(
        matching: Optional[Callable[[Entity], bool]] = None,
        max_distance: float = 64.0,
    ) -> Optional[Entity]:
        return bot.entity_tracker.nearest_entity(
            matching=matching,
            origin=bot.entity.position,
            max_distance=max_distance,
        )

    bot.nearest_entity = nearest_entity  # type: ignore
