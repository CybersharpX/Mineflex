"""Vehicle interaction (mount, dismount)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mineflex.constants import Hand, InteractType
from mineflex.entity.entity import Entity
from mineflex.protocol.packets.play.entities import InteractPacket

if TYPE_CHECKING:
    from mineflex.bot import Bot


class VehicleManager:
    """Manages riding entities such as boats, minecarts, and horses."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def mount(self, entity: Entity) -> None:
        """Mount a rideable vehicle entity."""
        packet = InteractPacket(
            entity_id=entity.id,
            interact_type=InteractType.INTERACT,
            hand=int(Hand.MAIN_HAND),
            sneaking=False,
        )
        await self.bot.client.send_packet(packet)
        self.bot.entity.vehicle = entity
        await self.bot.emit("mount", entity)

    async def dismount(self) -> None:
        """Dismount current vehicle by sneaking."""
        if self.bot.entity.vehicle is not None:
            # Sneak to dismount
            self.bot.physics.controls.sneak = True
            veh = self.bot.entity.vehicle
            self.bot.entity.vehicle = None
            await self.bot.emit("dismount", veh)
            self.bot.physics.controls.sneak = False
