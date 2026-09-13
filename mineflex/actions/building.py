"""Block placement and construction actions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mineflex.constants import BlockFace, Hand
from mineflex.errors import PlacementError
from mineflex.protocol.packets.play.player import SwingArmPacket, UseItemOnPacket
from mineflex.types import Vec3
from mineflex.world.block import Block

if TYPE_CHECKING:
    from mineflex.bot import Bot


class BuildingManager:
    """Manages placing blocks against existing world blocks."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def place_block(
        self,
        reference_block: Block,
        face_vector: Vec3,
        hand: Hand = Hand.MAIN_HAND,
    ) -> None:
        """Place held item against a face of the reference block."""
        held = self.bot.inventory.selected_item
        if held is None or held.count <= 0:
            raise PlacementError("No item in hand to place")

        player_pos = self.bot.entity.position
        dist = player_pos.distance_to(reference_block.position)
        if dist > 5.0:
            raise PlacementError(f"Reference block is out of reach ({dist:.2f} > 5.0)")

        # Determine BlockFace enum
        face = BlockFace.TOP
        if face_vector.y > 0:
            face = BlockFace.TOP
        elif face_vector.y < 0:
            face = BlockFace.BOTTOM
        elif face_vector.z < 0:
            face = BlockFace.NORTH
        elif face_vector.z > 0:
            face = BlockFace.SOUTH
        elif face_vector.x < 0:
            face = BlockFace.WEST
        elif face_vector.x > 0:
            face = BlockFace.EAST

        # Cursor placement position on block face (0.0 to 1.0)
        cursor_x = 0.5 + face_vector.x * 0.5
        cursor_y = 0.5 + face_vector.y * 0.5
        cursor_z = 0.5 + face_vector.z * 0.5

        packet = UseItemOnPacket(
            hand=int(hand),
            pos=reference_block.position.floored(),
            face=face,
            cursor_x=float(cursor_x),
            cursor_y=float(cursor_y),
            cursor_z=float(cursor_z),
            inside_block=False,
            sequence=0,
        )

        await self.bot.client.send_packet(packet)
        await self.bot.client.send_packet(SwingArmPacket(hand=hand))
        await self.bot.emit("block_placed", reference_block, face_vector)
