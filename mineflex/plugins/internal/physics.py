"""Internal plugin integrating the physics engine and movement simulation loop."""

from __future__ import annotations

import asyncio
import math
from typing import TYPE_CHECKING

from mineflex.constants import PHYSICS_TICK_INTERVAL
from mineflex.physics.engine import PhysicsEngine
from mineflex.protocol.packets.play.player import (
    ConfirmTeleportPacket,
    SetPlayerPositionAndRotationPacket,
    SynchronizePositionPacket,
)
from mineflex.types import Vec3

if TYPE_CHECKING:
    from mineflex.bot import Bot


def inject_physics(bot: Bot) -> None:
    """Inject physics simulation, movement controls, and positioning into bot."""
    bot.physics = PhysicsEngine()
    bot.physics_enabled = getattr(bot, "physics_enabled", True)
    bot._physics_task: asyncio.Task | None = None
    bot._spawned = False

    async def on_sync_position(packet: SynchronizePositionPacket) -> None:
        bot.physics.position = Vec3(packet.x, packet.y, packet.z)
        bot.physics.yaw = packet.yaw
        bot.physics.pitch = packet.pitch
        bot.entity.position = bot.physics.position
        bot.entity.yaw = packet.yaw
        bot.entity.pitch = packet.pitch

        # Confirm teleportation with server
        await bot.client.send_packet(ConfirmTeleportPacket(teleport_id=packet.teleport_id))

        if not bot._spawned:
            bot._spawned = True
            await bot.emit("spawn")
            # Start 20 Hz physics loop
            if bot.physics_enabled and bot._physics_task is None:
                bot._physics_task = asyncio.create_task(_physics_loop(bot))
        else:
            await bot.emit("forced_move", bot.entity.position)

    bot.client.register_handler(SynchronizePositionPacket, on_sync_position)

    def set_control_state(control: str, state: bool) -> None:
        """Set movement control state (forward, back, left, right, jump, sprint, sneak)."""
        if hasattr(bot.physics.controls, control):
            setattr(bot.physics.controls, control, bool(state))
        else:
            raise ValueError(f"Unknown control state: {control}")

    def clear_control_states() -> None:
        """Reset all movement controls."""
        bot.physics.controls.reset()

    async def look(yaw: float, pitch: float, force: bool = False) -> None:
        """Update bot viewing angle in degrees."""
        bot.physics.yaw = yaw
        bot.physics.pitch = pitch
        bot.entity.yaw = yaw
        bot.entity.pitch = pitch

        if bot.client and bot.client.is_connected:
            packet = SetPlayerPositionAndRotationPacket(
                x=bot.entity.position.x,
                y=bot.entity.position.y,
                z=bot.entity.position.z,
                yaw=yaw,
                pitch=pitch,
                on_ground=bot.entity.on_ground,
            )
            await bot.client.send_packet(packet)

    async def look_at(target: Vec3, force: bool = False) -> None:
        """Rotate bot head towards target 3D coordinates."""
        eye_pos = bot.entity.eye_position
        dx = target.x - eye_pos.x
        dy = target.y - eye_pos.y
        dz = target.z - eye_pos.z

        horiz_dist = math.sqrt(dx * dx + dz * dz)
        yaw_rad = -math.atan2(dx, dz)
        pitch_rad = -math.atan2(dy, horiz_dist)

        yaw = math.degrees(yaw_rad)
        pitch = math.degrees(pitch_rad)
        await look(yaw, pitch, force=force)

    bot.set_control_state = set_control_state  # type: ignore
    bot.clear_control_states = clear_control_states  # type: ignore
    bot.look = look  # type: ignore
    bot.look_at = look_at  # type: ignore


async def _physics_loop(bot: Bot) -> None:
    """Run 20 Hz physics simulation loop."""
    try:
        while bot.client and bot.client.is_connected and bot.physics_enabled:
            bot.physics.tick(bot.world)

            bot.entity.position = bot.physics.position
            bot.entity.velocity = bot.physics.velocity
            bot.entity.yaw = bot.physics.yaw
            bot.entity.pitch = bot.physics.pitch
            bot.entity.on_ground = bot.physics.on_ground

            # Send movement packet to server
            packet = SetPlayerPositionAndRotationPacket(
                x=bot.entity.position.x,
                y=bot.entity.position.y,
                z=bot.entity.position.z,
                yaw=bot.entity.yaw,
                pitch=bot.entity.pitch,
                on_ground=bot.entity.on_ground,
            )
            try:
                await bot.client.send_packet(packet)
            except Exception:
                break

            await bot.emit("physics_tick")
            await asyncio.sleep(PHYSICS_TICK_INTERVAL)
    except asyncio.CancelledError:
        pass
