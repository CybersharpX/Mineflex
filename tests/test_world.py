"""Unit tests for world state, chunk sections, and block queries."""

from mineflex.data import Registry
from mineflex.types import AABB, Vec3
from mineflex.world import Chunk, ChunkSection, World


def test_chunk_section_get_set():
    section = ChunkSection()
    assert section.get_block_state(0, 0, 0) == 0
    assert section.block_count == 0

    section.set_block_state(5, 7, 9, 14)  # cobblestone
    assert section.get_block_state(5, 7, 9) == 14
    assert section.block_count == 1

    section.set_block_state(5, 7, 9, 0)  # air
    assert section.get_block_state(5, 7, 9) == 0
    assert section.block_count == 0


def test_chunk_column_get_set():
    chunk = Chunk(chunk_x=0, chunk_z=0)
    # Test block at Y=-60 (negative coordinate in section 0)
    chunk.set_block_state(2, -60, 4, 1)  # stone
    assert chunk.get_block_state(2, -60, 4) == 1

    # Test block at Y=64 (section 8)
    chunk.set_block_state(10, 64, 10, 8)  # grass_block
    assert chunk.get_block_state(10, 64, 10) == 8


def test_world_block_access_and_queries():
    reg = Registry("1.20.1")
    world = World(registry=reg)

    pos1 = Vec3(10, 64, 10)
    world.set_block_state(pos1, 8)  # grass_block

    block = world.get_block(pos1)
    assert block.name == "grass_block"
    assert block.solid is True
    assert block.is_air is False
    assert block.hardness == 0.6

    pos2 = Vec3(10, 65, 10)
    air_block = world.get_block(pos2)
    assert air_block.is_air is True

    # Spatial queries
    found_blocks = world.find_blocks("grass_block", point=Vec3(10, 64, 10), max_distance=5)
    assert len(found_blocks) == 1
    assert found_blocks[0] == Vec3(10, 64, 10)

    closest = world.find_block("grass_block", point=Vec3(12, 64, 12), max_distance=5)
    assert closest is not None
    assert closest.name == "grass_block"


def test_world_collision_boxes():
    world = World()
    # Place a solid block at (5, 64, 5)
    world.set_block_state(Vec3(5, 64, 5), 1)  # stone

    # Test intersecting player bounding box
    player_box = AABB(4.8, 64.0, 4.8, 5.4, 65.8, 5.4)
    colliding = world.get_colliding_bounding_boxes(player_box)
    assert len(colliding) == 1
    assert colliding[0].min_x == 5.0
    assert colliding[0].min_y == 64.0
    assert colliding[0].min_z == 5.0

    # Non-intersecting box
    non_colliding = AABB(0, 0, 0, 1, 1, 1)
    assert len(world.get_colliding_bounding_boxes(non_colliding)) == 0
