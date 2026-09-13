"""Unit tests for the standalone physics simulation engine."""

import math

from mineflex.physics import PhysicsEngine
from mineflex.types import Vec3
from mineflex.world import World


def test_free_fall_gravity():
    world = World()
    # Bot starts high in the air at Y=100
    engine = PhysicsEngine(position=Vec3(0, 100, 0))

    assert engine.position.y == 100.0
    assert engine.on_ground is False

    # Simulate 10 ticks of free-fall
    engine.simulate_ticks(world, 10)

    assert engine.position.y < 100.0
    assert engine.velocity.y < 0.0
    assert engine.on_ground is False


def test_ground_collision_and_landing():
    world = World()
    # Place a solid ground block at (0, 60, 0)
    world.set_block_state(Vec3(0, 60, 0), 1)  # stone

    # Spawn bot just above ground at Y=62.0
    engine = PhysicsEngine(position=Vec3(0.5, 62.0, 0.5))

    # Simulate 20 ticks
    engine.simulate_ticks(world, 20)

    # Bot should land on the top face of the block (Y=61.0)
    assert math.isclose(engine.position.y, 61.0, abs_tol=0.01)
    assert engine.on_ground is True
    assert engine.velocity.y == 0.0


def test_jump_mechanics():
    world = World()
    # Solid ground at (0, 60, 0)
    world.set_block_state(Vec3(0, 60, 0), 1)

    engine = PhysicsEngine(position=Vec3(0.5, 61.0, 0.5))
    engine.on_ground = True
    engine.controls.jump = True

    # Single tick of jumping
    engine.tick(world)

    # Bot should be ascending
    assert engine.position.y > 61.0
    assert engine.velocity.y > 0.0
    assert engine.on_ground is False


def test_horizontal_movement_controls():
    world = World()
    # Create flat surface along Z axis
    for z in range(-5, 15):
        world.set_block_state(Vec3(0, 60, z), 1)

    engine = PhysicsEngine(position=Vec3(0.5, 61.0, 0.5), yaw=0.0)  # yaw 0 = +Z
    engine.on_ground = True
    engine.controls.forward = True

    engine.simulate_ticks(world, 10)

    # Bot moved forward in +Z direction
    assert engine.position.z > 0.5
    assert math.isclose(engine.position.y, 61.0, abs_tol=0.01)


def test_auto_stepping():
    world = World()
    # Floor at Y=60
    for x in range(-2, 4):
        for z in range(-2, 20):
            world.set_block_state(Vec3(x, 60, z), 1)

    engine = PhysicsEngine(position=Vec3(0.5, 61.0, 0.5), yaw=0.0)
    engine.step_height = 1.1  # Allow stepping 1 block for test
    engine.on_ground = True
    engine.controls.forward = True

    # Place a 1-block obstacle right in front at (0, 61, 2)
    world.set_block_state(Vec3(0, 61, 2), 1)
    # Put floor behind it at (0, 61, z) for z >= 2
    for z in range(2, 20):
        world.set_block_state(Vec3(0, 61, z), 1)

    # Simulate 25 ticks
    engine.simulate_ticks(world, 25)

    # Bot stepped up onto Y=62 and is on ground on top of the obstacle platform
    assert engine.position.z > 2.0
    assert math.isclose(engine.position.y, 62.0, abs_tol=0.05)
    assert engine.on_ground is True


def test_liquid_water_and_lava_physics():
    world = World()
    # Water column around Y=60 to 65
    for y in range(60, 66):
        world.set_block_state(Vec3(0, y, 0), 26)

    engine = PhysicsEngine(position=Vec3(0.5, 64.0, 0.5))
    engine.velocity = Vec3(0, -0.5, 0)
    engine.tick(world)

    # In water, terminal descent is dampened and drag is applied
    assert engine.velocity.y > -0.5

    # Jumping in water swims upward
    engine.controls.jump = True
    engine.tick(world)
    assert engine.velocity.y > 0.0


def test_climbing_ladder_physics():
    world = World()
    # Ladder block at Y=64 (ladder default_state_id is 260)
    world.set_block_state(Vec3(0, 64, 0), 260)

    engine = PhysicsEngine(position=Vec3(0.5, 64.0, 0.5))
    engine.controls.forward = True
    engine.tick(world)

    # Ascends on ladder with forward pressed
    assert engine.velocity.y >= 0.14


def test_knockback_impulse():
    engine = PhysicsEngine(position=Vec3(0, 64, 0))
    assert engine.velocity.x == 0.0

    engine.apply_knockback(Vec3(1.5, 0.4, -0.8))
    assert engine.velocity.x == 1.5
    assert engine.velocity.y == 0.4
    assert engine.velocity.z == -0.8
