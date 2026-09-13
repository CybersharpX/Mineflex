"""Internal plugin for world blocks and chunk tracking."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Callable, List, Optional, Union

from mineflex.protocol.packets.play.world import BlockUpdatePacket, ChunkDataPacket
from mineflex.types import Position, Vec3
from mineflex.world.block import Block
from mineflex.world.world import World

if TYPE_CHECKING:
    from mineflex.bot import Bot


def inject_blocks(bot: Bot) -> None:
    """Inject world block state and spatial lookup methods into bot."""
    bot.world = World(registry=bot.registry)

    def on_chunk_data(packet: ChunkDataPacket) -> None:
        chunk = bot.world.load_chunk_packet(packet)
        bot.emit_sync("chunk_column_load", chunk)

    def on_block_update(packet: BlockUpdatePacket) -> None:
        old_block = bot.world.get_block(packet.pos)
        bot.world.set_block_state(packet.pos, packet.block_state_id)
        new_block = bot.world.get_block(packet.pos)
        bot.emit_sync("block_update", old_block, new_block)

    bot.client.register_handler(ChunkDataPacket, on_chunk_data)
    bot.client.register_handler(BlockUpdatePacket, on_block_update)

    def block_at(pos: Union[Vec3, Position]) -> Block:
        return bot.world.get_block(pos)

    def find_blocks(
        matching: Union[str, int, Callable[[Block], bool]],
        point: Optional[Vec3] = None,
        max_distance: int = 16,
        count: int = 100,
    ) -> List[Vec3]:
        orig = point or bot.entity.position
        return bot.world.find_blocks(matching, orig, max_distance=max_distance, count=count)

    def find_block(
        matching: Union[str, int, Callable[[Block], bool]],
        point: Optional[Vec3] = None,
        max_distance: int = 16,
    ) -> Optional[Block]:
        orig = point or bot.entity.position
        return bot.world.find_block(matching, orig, max_distance=max_distance)

    def block_at_cursor(max_distance: float = 4.5) -> Optional[Block]:
        """Get the block the bot is currently looking at."""
        yaw_rad = math.radians(bot.entity.yaw)
        pitch_rad = math.radians(bot.entity.pitch)
        dx = -math.sin(yaw_rad) * math.cos(pitch_rad)
        dy = -math.sin(pitch_rad)
        dz = math.cos(yaw_rad) * math.cos(pitch_rad)
        dir_vec = Vec3(dx, dy, dz)
        hit = bot.world.raycast(bot.entity.eye_position, dir_vec, max_distance=max_distance)
        return hit[0] if hit else None

    def can_see_block(block: Block, max_distance: float = 4.5) -> bool:
        """Check if bot has an unobstructed line of sight to target block."""
        eye_pos = bot.entity.eye_position
        target_pos = block.position + Vec3(0.5, 0.5, 0.5)
        diff = target_pos - eye_pos
        dist = diff.length()
        if dist > max_distance:
            return False
        if dist == 0:
            return True
        hit = bot.world.raycast(eye_pos, diff.normalize(), max_distance=dist + 0.05)
        if hit is None:
            return True
        return hit[0].position == block.position

    bot.block_at = block_at  # type: ignore
    bot.find_blocks = find_blocks  # type: ignore
    bot.find_block = find_block  # type: ignore
    bot.block_at_cursor = block_at_cursor  # type: ignore
    bot.block_in_sight = block_at_cursor  # type: ignore
    bot.can_see_block = can_see_block  # type: ignore
