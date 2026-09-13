"""Block digging action state machine and duration calculation."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, Optional

from mineflex.constants import BlockFace, DiggingStatus, Hand
from mineflex.errors import DiggingError
from mineflex.protocol.packets.play.player import PlayerActionPacket, SwingArmPacket
from mineflex.world.block import Block

if TYPE_CHECKING:
    from mineflex.bot import Bot


class DiggingManager:
    """Manages asynchronous block digging operations."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.target_block: Optional[Block] = None
        self._dig_task: Optional[asyncio.Task] = None

    async def dig(self, block: Block, force_look: bool = True) -> None:
        """Start digging the given block, awaiting completion or cancellation."""
        if not block.diggable or block.is_air:
            raise DiggingError(f"Block {block.name} is not diggable")

        # Reach distance check
        player_pos = self.bot.entity.position
        dist = player_pos.distance_to(block.position)
        if dist > 5.0:
            raise DiggingError(f"Block at {block.position} is out of reach ({dist:.2f} > 5.0)")

        if self.target_block is not None:
            await self.stop_digging()

        if force_look:
            await self.bot.look_at(block.position.offset(0.5, 0.5, 0.5))

        self.target_block = block
        self._dig_task = asyncio.create_task(self._perform_dig(block))
        try:
            await self._dig_task
        except asyncio.CancelledError:
            await self._send_cancel(block)
            raise
        finally:
            self.target_block = None
            self._dig_task = None

    async def stop_digging(self) -> None:
        """Cancel ongoing digging operation."""
        if self._dig_task and not self._dig_task.done():
            self._dig_task.cancel()
            try:
                await self._dig_task
            except (asyncio.CancelledError, Exception):
                pass
            self.target_block = None
            self._dig_task = None

    async def _send_cancel(self, block: Block) -> None:
        if self.bot.client and self.bot.client.is_connected:
            cancel_pkt = PlayerActionPacket(
                status=DiggingStatus.CANCELLED_DIGGING,
                pos=block.position.floored(),
                face=BlockFace.TOP,
                sequence=0,
            )
            await self.bot.client.send_packet(cancel_pkt)
            await self.bot.emit("digging_aborted", block)

    async def _perform_dig(self, block: Block) -> None:
        # Calculate digging duration
        held_item = self.bot.inventory.selected_item
        duration = self.calculate_dig_time(block, held_item)

        # 1. Send started digging packet
        start_pkt = PlayerActionPacket(
            status=DiggingStatus.STARTED_DIGGING,
            pos=block.position.floored(),
            face=BlockFace.TOP,
            sequence=0,
        )
        await self.bot.client.send_packet(start_pkt)
        await self.bot.client.send_packet(SwingArmPacket(hand=Hand.MAIN_HAND))
        await self.bot.emit("digging_started", block)

        # 2. Wait for digging time
        await asyncio.sleep(duration)

        # 3. Send finished digging packet
        finish_pkt = PlayerActionPacket(
            status=DiggingStatus.FINISHED_DIGGING,
            pos=block.position.floored(),
            face=BlockFace.TOP,
            sequence=0,
        )
        await self.bot.client.send_packet(finish_pkt)
        await self.bot.emit("digging_completed", block)

    @staticmethod
    def calculate_dig_time(block: Block, held_item: Optional[Any] = None) -> float:
        """Calculate mining duration in seconds based on hardness and tool efficiency."""
        if block.hardness <= 0:
            return 0.05

        multiplier = 1.0
        if held_item and any(tool in held_item.name for tool in block.definition.harvest_tools):
            multiplier = 4.0

        dig_time = (block.hardness * 1.5) / multiplier
        return max(0.05, min(dig_time, 15.0))
