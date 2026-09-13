"""Internal plugin for entity tracking and tablist players."""

from __future__ import annotations

import math
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
from mineflex.types import Vec3

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

    def entity_at_cursor(max_distance: float = 4.5) -> Optional[Entity]:
        """Find the closest entity intersected by the bot's look vector."""
        eye_pos = bot.entity.eye_position
        yaw_rad = math.radians(bot.entity.yaw)
        pitch_rad = math.radians(bot.entity.pitch)
        dx = -math.sin(yaw_rad) * math.cos(pitch_rad)
        dy = -math.sin(pitch_rad)
        dz = math.cos(yaw_rad) * math.cos(pitch_rad)
        dir_vec = Vec3(dx, dy, dz)

        best_entity: Optional[Entity] = None
        best_dist = max_distance

        def _axis_bounds(min_v: float, max_v: float, p: float, d: float) -> tuple[float, float]:
            if d != 0:
                t1 = (min_v - p) / d
                t2 = (max_v - p) / d
                return (min(t1, t2), max(t1, t2))
            if min_v <= p <= max_v:
                return (-float("inf"), float("inf"))
            return (float("inf"), -float("inf"))

        for entity in bot.entities.values():
            if entity.id == bot.entity.id:
                continue
            box = entity.bounding_box
            t_min, t_max = _axis_bounds(box.min_x, box.max_x, eye_pos.x, dir_vec.x)
            ty_min, ty_max = _axis_bounds(box.min_y, box.max_y, eye_pos.y, dir_vec.y)

            if t_min > ty_max or ty_min > t_max:
                continue

            t_near = max(t_min, ty_min)
            t_far = min(t_max, ty_max)

            tz_min, tz_max = _axis_bounds(box.min_z, box.max_z, eye_pos.z, dir_vec.z)
            if t_near > tz_max or tz_min > t_far:
                continue

            t_entry = max(t_near, tz_min)
            if 0 < t_entry < best_dist:
                best_dist = t_entry
                best_entity = entity

        return best_entity

    bot.nearest_entity = nearest_entity  # type: ignore
    bot.entity_at_cursor = entity_at_cursor  # type: ignore
