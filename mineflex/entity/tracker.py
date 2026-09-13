"""Entity tracker managing entity states and lifecycle events."""

from __future__ import annotations

import uuid
from typing import Callable, Dict, Optional

from mineflex.data.provider import Registry
from mineflex.entity.entity import Entity
from mineflex.entity.player import Player
from mineflex.events.emitter import AsyncEventEmitter
from mineflex.protocol.packets.play.entities import (
    DestroyEntitiesPacket,
    SetEntityVelocityPacket,
    SpawnEntityPacket,
    UpdateEntityPositionPacket,
    UpdateEntityPositionRotationPacket,
    UpdateEntityRotationPacket,
)
from mineflex.types import Vec3


class EntityTracker:
    """Manages all tracked entities and player tablist state in the world."""

    def __init__(
        self, registry: Optional[Registry] = None, emitter: Optional[AsyncEventEmitter] = None
    ) -> None:
        self.registry = registry or Registry("1.20.1")
        self.emitter = emitter or AsyncEventEmitter()
        self.entities: Dict[int, Entity] = {}
        self.players: Dict[str, Player] = {}
        self.players_by_uuid: Dict[uuid.UUID, Player] = {}

    def spawn_entity(self, packet: SpawnEntityPacket) -> Entity:
        """Create or update an entity from a SpawnEntity packet."""
        e_def = self.registry.entities.get(packet.entity_type)
        name = e_def.name if e_def else f"entity_{packet.entity_type}"
        category = e_def.category if e_def else "unknown"
        width = e_def.width if e_def else 0.6
        height = e_def.height if e_def else 1.8

        entity = Entity(
            id=packet.entity_id,
            uuid=packet.entity_uuid,
            type=packet.entity_type,
            name=name,
            category=category,
            position=Vec3(packet.x, packet.y, packet.z),
            velocity=Vec3(packet.vel_x / 8000.0, packet.vel_y / 8000.0, packet.vel_z / 8000.0),
            yaw=packet.yaw,
            pitch=packet.pitch,
            head_yaw=packet.head_yaw,
            width=width,
            height=height,
        )

        self.entities[packet.entity_id] = entity

        # Link player entity if matching UUID exists
        if packet.entity_uuid in self.players_by_uuid:
            self.players_by_uuid[packet.entity_uuid].entity = entity

        self.emitter.emit_sync("entity_spawn", entity)
        return entity

    def update_position(self, packet: UpdateEntityPositionPacket) -> Optional[Entity]:
        entity = self.entities.get(packet.entity_id)
        if entity is None:
            return None

        # Protocol short deltas: delta / 4096 = blocks
        dx = packet.delta_x / 4096.0
        dy = packet.delta_y / 4096.0
        dz = packet.delta_z / 4096.0

        entity.position = entity.position.offset(dx, dy, dz)
        entity.on_ground = packet.on_ground
        self.emitter.emit_sync("entity_moved", entity)
        return entity

    def update_position_rotation(
        self, packet: UpdateEntityPositionRotationPacket
    ) -> Optional[Entity]:
        entity = self.entities.get(packet.entity_id)
        if entity is None:
            return None

        dx = packet.delta_x / 4096.0
        dy = packet.delta_y / 4096.0
        dz = packet.delta_z / 4096.0

        entity.position = entity.position.offset(dx, dy, dz)
        entity.yaw = packet.yaw
        entity.pitch = packet.pitch
        entity.on_ground = packet.on_ground
        self.emitter.emit_sync("entity_moved", entity)
        return entity

    def update_rotation(self, packet: UpdateEntityRotationPacket) -> Optional[Entity]:
        entity = self.entities.get(packet.entity_id)
        if entity is None:
            return None

        entity.yaw = packet.yaw
        entity.pitch = packet.pitch
        entity.on_ground = packet.on_ground
        self.emitter.emit_sync("entity_moved", entity)
        return entity

    def update_velocity(self, packet: SetEntityVelocityPacket) -> Optional[Entity]:
        entity = self.entities.get(packet.entity_id)
        if entity is None:
            return None

        entity.velocity = Vec3(
            packet.vel_x / 8000.0,
            packet.vel_y / 8000.0,
            packet.vel_z / 8000.0,
        )
        return entity

    def destroy_entities(self, packet: DestroyEntitiesPacket) -> None:
        for eid in packet.entity_ids:
            entity = self.entities.pop(eid, None)
            if entity:
                if entity.uuid in self.players_by_uuid:
                    self.players_by_uuid[entity.uuid].entity = None
                self.emitter.emit_sync("entity_gone", entity)

    def nearest_entity(
        self,
        matching: Optional[Callable[[Entity], bool]] = None,
        origin: Optional[Vec3] = None,
        max_distance: float = 64.0,
    ) -> Optional[Entity]:
        """Find the nearest entity matching an optional filter within max_distance."""
        orig = origin or Vec3(0, 0, 0)
        best_entity: Optional[Entity] = None
        best_dist_sq = max_distance * max_distance

        for entity in self.entities.values():
            if matching is not None and not matching(entity):
                continue
            dist_sq = entity.position.distance_squared(orig)
            if dist_sq < best_dist_sq:
                best_dist_sq = dist_sq
                best_entity = entity

        return best_entity
