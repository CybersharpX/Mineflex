"""Stand-alone Minecraft physics engine supporting gravity, collision, jumping, and friction."""

from __future__ import annotations

import math
from typing import Optional

from mineflex.constants import (
    PHYSICS_AIR_DRAG,
    PHYSICS_DEFAULT_SLIPPERINESS,
    PHYSICS_GRAVITY,
    PHYSICS_JUMP_VELOCITY,
    PHYSICS_SNEAK_SPEED_MULT,
    PHYSICS_SPRINT_SPEED_BOOST,
    PHYSICS_STEP_HEIGHT,
    PHYSICS_TERMINAL_VELOCITY,
    PLAYER_HEIGHT,
    PLAYER_SNEAK_HEIGHT,
    PLAYER_WIDTH,
)
from mineflex.physics.collision import resolve_collision
from mineflex.physics.controls import ControlState
from mineflex.types import AABB, Vec3
from mineflex.world.world import World


class PhysicsEngine:
    """Simulates 20 Hz Minecraft player physics."""

    def __init__(
        self,
        position: Optional[Vec3] = None,
        velocity: Optional[Vec3] = None,
        yaw: float = 0.0,
        pitch: float = 0.0,
    ) -> None:
        self.position = position or Vec3(0, 64, 0)
        self.velocity = velocity or Vec3(0, 0, 0)
        self.yaw = yaw
        self.pitch = pitch
        self.on_ground = False
        self.is_collided_horizontally = False
        self.controls = ControlState()
        self.step_height = PHYSICS_STEP_HEIGHT

    @property
    def bounding_box(self) -> AABB:
        height = PLAYER_SNEAK_HEIGHT if self.controls.sneak else PLAYER_HEIGHT
        return AABB.from_entity(self.position, PLAYER_WIDTH, height)

    def tick(self, world: World) -> None:
        """Simulate one physics tick (50ms)."""
        # 1. Handle jumping
        if self.controls.jump and self.on_ground:
            self.velocity = Vec3(self.velocity.x, PHYSICS_JUMP_VELOCITY, self.velocity.z)
            if self.controls.sprint:
                yaw_rad = math.radians(self.yaw)
                self.velocity = self.velocity.offset(
                    -math.sin(yaw_rad) * 0.2, 0.0, math.cos(yaw_rad) * 0.2
                )

        # 2. Calculate horizontal acceleration from controls
        strafe = 0.0
        forward = 0.0
        if self.controls.forward:
            forward += 1.0
        if self.controls.back:
            forward -= 1.0
        if self.controls.left:
            strafe -= 1.0
        if self.controls.right:
            strafe += 1.0

        # Base speed in blocks/tick
        speed = 0.1
        if self.controls.sprint:
            speed *= PHYSICS_SPRINT_SPEED_BOOST
        elif self.controls.sneak:
            speed *= PHYSICS_SNEAK_SPEED_MULT

        if forward != 0.0 or strafe != 0.0:
            move_norm = math.sqrt(forward * forward + strafe * strafe)
            forward /= move_norm
            strafe /= move_norm

            yaw_rad = math.radians(self.yaw)
            sin_yaw = math.sin(yaw_rad)
            cos_yaw = math.cos(yaw_rad)

            # Move direction vectors
            acc_x = (strafe * cos_yaw - forward * sin_yaw) * speed
            acc_z = (forward * cos_yaw + strafe * sin_yaw) * speed
            self.velocity = self.velocity.offset(acc_x, 0.0, acc_z)

        # 3. Apply gravity and fluid / climbable physics
        block_at_player = world.get_block(self.position)
        in_water = block_at_player.name == "water"
        in_lava = block_at_player.name == "lava"
        is_climbing = block_at_player.name in ("ladder", "vine", "scaffolding")

        if is_climbing:
            if forward > 0 or self.controls.jump:
                new_vy = 0.15
            elif self.controls.sneak:
                new_vy = 0.0
            else:
                new_vy = max(self.velocity.y, -0.15)
            self.velocity = Vec3(self.velocity.x * 0.8, new_vy, self.velocity.z * 0.8)
        elif in_water:
            self.velocity = Vec3(
                self.velocity.x * 0.8,
                max(self.velocity.y * 0.8 - 0.02, -0.15),
                self.velocity.z * 0.8,
            )
            if self.controls.jump:
                self.velocity = Vec3(self.velocity.x, 0.04, self.velocity.z)
        elif in_lava:
            self.velocity = Vec3(
                self.velocity.x * 0.5,
                max(self.velocity.y * 0.5 - 0.02, -0.1),
                self.velocity.z * 0.5,
            )
            if self.controls.jump:
                self.velocity = Vec3(self.velocity.x, 0.02, self.velocity.z)
        else:
            new_vy = max(self.velocity.y - PHYSICS_GRAVITY, -PHYSICS_TERMINAL_VELOCITY)
            self.velocity = Vec3(self.velocity.x, new_vy, self.velocity.z)

        # 4. Resolve collisions and stepping
        adjusted_vel, on_ground, collided_horiz = resolve_collision(
            self.bounding_box,
            self.velocity,
            world,
            step_height=self.step_height,
            is_on_ground=self.on_ground,
        )

        # Sneaking ledge containment: avoid falling off ledges if crouching
        if self.controls.sneak and self.on_ground:
            test_pos = self.position + Vec3(adjusted_vel.x, -0.6, adjusted_vel.z)
            block_below = world.get_block(test_pos)
            if block_below.is_air:
                adjusted_vel = Vec3(0.0, adjusted_vel.y, 0.0)

        self.position = self.position + adjusted_vel
        self.on_ground = on_ground
        self.is_collided_horizontally = collided_horiz

        # If landed or hit ceiling, zero vertical velocity
        final_vy = 0.0 if (self.velocity.y != adjusted_vel.y) else adjusted_vel.y

        # 5. Apply friction & drag
        if self.on_ground:
            friction = PHYSICS_DEFAULT_SLIPPERINESS * 0.91
        else:
            friction = PHYSICS_AIR_DRAG

        self.velocity = Vec3(
            adjusted_vel.x * friction,
            final_vy * PHYSICS_AIR_DRAG,
            adjusted_vel.z * friction,
        )

    def apply_knockback(self, knockback: Vec3) -> None:
        """Apply an external knockback impulse to the entity's velocity."""
        self.velocity = self.velocity + knockback

    def simulate_ticks(self, world: World, ticks: int) -> None:
        """Simulate a specified number of physics ticks."""
        for _ in range(ticks):
            self.tick(world)
