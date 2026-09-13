"""Internal plugin for inventory and container window management."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Union

from mineflex.constants import DiggingStatus
from mineflex.errors import InventoryError
from mineflex.inventory.container import ChestWindow, CraftingTableWindow, FurnaceWindow
from mineflex.inventory.item import Item
from mineflex.inventory.window import PlayerInventory, Window
from mineflex.protocol.packets.play.inventory import (
    ClickContainerPacket,
    CloseContainerClientboundPacket,
    OpenScreenPacket,
    SetContainerContentPacket,
    SetContainerSlotPacket,
    SetHeldItemPacket,
)
from mineflex.protocol.packets.play.player import PlayerActionPacket

if TYPE_CHECKING:
    from mineflex.bot import Bot


def inject_inventory(bot: Bot) -> None:
    """Inject inventory, slot manipulation, and container handling into bot."""
    bot.inventory = PlayerInventory()
    bot.current_window: Optional[Window] = None

    def on_set_container_content(packet: SetContainerContentPacket) -> None:
        target_win = bot.inventory if packet.window_id == 0 else bot.current_window
        if target_win is not None:
            for idx, slot_dict in enumerate(packet.items):
                item = Item.from_slot(slot_dict, registry=bot.registry) if slot_dict else None
                target_win.set_slot(idx, item)
            if packet.carried_item:
                target_win.carried_item = Item.from_slot(packet.carried_item, registry=bot.registry)
            else:
                target_win.carried_item = None
            bot.emit_sync("window_items", target_win)

    def on_set_container_slot(packet: SetContainerSlotPacket) -> None:
        item = Item.from_slot(packet.item, registry=bot.registry) if packet.item else None
        if packet.window_id == -1:
            if bot.current_window:
                bot.current_window.carried_item = item
            bot.inventory.carried_item = item
        elif packet.window_id == 0:
            bot.inventory.set_slot(packet.slot, item)
            bot.emit_sync("set_slot", bot.inventory, packet.slot, item)
        elif bot.current_window and bot.current_window.id == packet.window_id:
            bot.current_window.set_slot(packet.slot, item)
            bot.emit_sync("set_slot", bot.current_window, packet.slot, item)

    def on_open_screen(packet: OpenScreenPacket) -> None:
        # Check window type
        if packet.window_type in (0, 1, 2, 3, 4, 5):  # Chest sizes
            win = ChestWindow(
                window_id=packet.window_id, title=packet.title, double=(packet.window_type >= 3)
            )
        elif packet.window_type == 11:
            win = CraftingTableWindow(window_id=packet.window_id, title=packet.title)
        elif packet.window_type == 13:
            win = FurnaceWindow(window_id=packet.window_id, title=packet.title)
        else:
            win = Window(
                window_id=packet.window_id, title=packet.title, window_type=packet.window_type
            )

        bot.current_window = win
        bot.emit_sync("window_open", win)

    def on_close_screen(packet: CloseContainerClientboundPacket) -> None:
        win = bot.current_window
        bot.current_window = None
        if win:
            bot.emit_sync("window_close", win)

    bot.client.register_handler(SetContainerContentPacket, on_set_container_content)
    bot.client.register_handler(SetContainerSlotPacket, on_set_container_slot)
    bot.client.register_handler(OpenScreenPacket, on_open_screen)
    bot.client.register_handler(CloseContainerClientboundPacket, on_close_screen)

    async def set_quick_bar_slot(slot_idx: int) -> None:
        """Select a hotbar slot (0 to 8)."""
        bot.inventory.set_selected_slot(slot_idx)
        if bot.client and bot.client.is_connected:
            await bot.client.send_packet(SetHeldItemPacket(slot=slot_idx))

    async def equip(item: Union[Item, str, int], destination: str = "hand") -> None:
        """Equip an item from inventory to specified destination."""
        match_name = item.name if isinstance(item, Item) else item
        found_slots = bot.inventory.find_items(match_name)
        if not found_slots:
            raise InventoryError(f"No item '{match_name}' found in inventory to equip")

        slot_idx, it = found_slots[0]
        if destination == "hand":
            # If in hotbar (36-44), select it directly
            if 36 <= slot_idx <= 44:
                await set_quick_bar_slot(slot_idx - 36)
            else:
                # Click to swap with selected hotbar slot
                target_slot = bot.inventory.selected_slot
                await click_slot(slot_idx, button=0, mode=0)
                await click_slot(target_slot, button=0, mode=0)

    async def click_slot(slot: int, button: int = 0, mode: int = 0) -> None:
        """Send Click Container packet to manipulate slots in current window or inventory."""
        target_win = bot.current_window or bot.inventory
        packet = ClickContainerPacket(
            window_id=target_win.id,
            state_id=0,
            slot=slot,
            button=button,
            mode=mode,
        )
        await bot.client.send_packet(packet)

    async def toss(item_id: int, count: int = 1) -> None:
        """Drop item from currently held slot."""
        status = DiggingStatus.DROP_ITEM_STACK if count > 1 else DiggingStatus.DROP_ITEM
        packet = PlayerActionPacket(
            status=status,
            pos=bot.entity.position.floored(),
            face=0,
            sequence=0,
        )
        await bot.client.send_packet(packet)

    bot.set_quick_bar_slot = set_quick_bar_slot  # type: ignore
    bot.equip = equip  # type: ignore
    bot.click_slot = click_slot  # type: ignore
    bot.toss = toss  # type: ignore
