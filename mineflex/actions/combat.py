"""Combat primitives (attacking, swinging)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mineflex.constants import Hand, InteractType
from mineflex.entity.entity import Entity
from mineflex.errors import InteractionError
from mineflex.protocol.packets.play.entities import InteractPacket
from mineflex.protocol.packets.play.player import SwingArmPacket

if TYPE_CHECKING:
    from mineflex.bot import Bot


class CombatManager:
    """Manages player attack primitives and target validation."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def attack(self, entity: Entity, swing: bool = True) -> None:
        """Attack a target entity with reach validation."""
        player_pos = self.bot.entity.position
        dist = player_pos.distance_to(entity.position)
        if dist > 4.5:
            raise InteractionError(f"Target entity {entity.id} is out of reach ({dist:.2f} > 4.5)")

        # Send Attack packet (InteractType 1 = ATTACK)
        packet = InteractPacket(
            entity_id=entity.id,
            interact_type=InteractType.ATTACK,
            sneaking=self.bot.physics.controls.sneak,
        )
        await self.bot.client.send_packet(packet)

        if swing:
            await self.bot.client.send_packet(SwingArmPacket(hand=Hand.MAIN_HAND))

        await self.bot.emit("attacked", entity)
