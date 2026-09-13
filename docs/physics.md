# Physics Engine Documentation

Mineflex features a standalone, deterministic 20 Hz physics simulation engine located in `mineflex.physics`.

---

## Capabilities

* **Gravity & Terminal Velocity**: Evaluates gravitational acceleration of -0.08 blocks/tick² clamped to a terminal velocity of -3.92 blocks/tick.
* **Friction & Drag**: Applies atmospheric drag (0.98 air drag) and ground friction (`slipperiness * 0.91`).
* **Jumping & Sprinting**: Implements +0.42 blocks/tick vertical jump impulse with horizontal directional sprint boosts.
* **Auto-Stepping**: Handles 0.6 block height stepping (stairs, slabs, or minor elevation differences) without requiring manual jump triggers.
* **AABB Block Collision**: Evaluates entity bounding box (0.6 x 1.8 blocks) against all solid block bounding boxes in the loaded world.

---

## Standalone Usage

The physics engine does not require an active network connection:

```python
from mineflex.physics import PhysicsEngine
from mineflex.types import Vec3
from mineflex.world import World

world = World()
world.set_block_state(Vec3(0, 60, 0), 1)  # stone ground at Y=60

engine = PhysicsEngine(position=Vec3(0.5, 62.0, 0.5))

# Simulate 20 ticks (1 second) of physics
engine.simulate_ticks(world, ticks=20)

print(f"Final position: {engine.position}")
print(f"On ground: {engine.on_ground}")
```
