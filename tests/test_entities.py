"""Unit tests for entity tracking and player management."""

import uuid

from mineflex.data import Registry
from mineflex.entity import EntityTracker
from mineflex.events.emitter import AsyncEventEmitter
from mineflex.protocol.packets.play.entities import (
    DestroyEntitiesPacket,
    SpawnEntityPacket,
    UpdateEntityPositionPacket,
)
from mineflex.types import Vec3


def test_entity_spawn_and_lifecycle():
    emitter = AsyncEventEmitter()
    reg = Registry("1.20.1")
    tracker = EntityTracker(registry=reg, emitter=emitter)

    spawned = []
    gone = []

    emitter.on("entity_spawn", lambda e: spawned.append(e))
    emitter.on("entity_gone", lambda e: gone.append(e))

    e_uuid = uuid.uuid4()
    spawn_packet = SpawnEntityPacket(
        entity_id=100,
        entity_uuid=e_uuid,
        entity_type=125,  # zombie
        x=10.0,
        y=64.0,
        z=10.0,
        pitch=0.0,
        yaw=90.0,
        head_yaw=90.0,
        data=0,
    )

    entity = tracker.spawn_entity(spawn_packet)
    assert entity.id == 100
    assert entity.name == "zombie"
    assert entity.category == "hostile"
    assert entity.position == Vec3(10.0, 64.0, 10.0)
    assert len(spawned) == 1

    # Update position (delta +4096 = +1 block)
    update_pos = UpdateEntityPositionPacket(
        entity_id=100,
        delta_x=4096,
        delta_y=0,
        delta_z=0,
        on_ground=True,
    )
    tracker.update_position(update_pos)
    assert entity.position.x == 11.0

    # Nearest entity query
    nearest = tracker.nearest_entity(origin=Vec3(11.0, 64.0, 10.0))
    assert nearest == entity

    # Destroy entity
    tracker.destroy_entities(DestroyEntitiesPacket(entity_ids=[100]))
    assert 100 not in tracker.entities
    assert len(gone) == 1
