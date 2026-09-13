"""Internal plugin for world blocks and chunk tracking."""

from __future__ import annotations

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

    bot.block_at = block_at  # type: ignore
    bot.find_blocks = find_blocks  # type: ignore
    bot.find_block = find_block  # type: ignore
