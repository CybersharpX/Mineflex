"""Internal plugin for inventory and container window management."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, List, Optional, Union

from mineflex.constants import BlockFace, DiggingStatus, Hand
from mineflex.data.provider import RecipeDefinition
from mineflex.errors import CraftingError, InventoryError
from mineflex.inventory.container import ChestWindow, CraftingTableWindow, FurnaceWindow
from mineflex.inventory.item import Item
from mineflex.inventory.window import PlayerInventory, Window
from mineflex.protocol.packets.play.inventory import (
    ClickContainerPacket,
    CloseContainerClientboundPacket,
    CloseContainerServerboundPacket,
    OpenScreenPacket,
    SetContainerContentPacket,
    SetContainerSlotPacket,
    SetHeldItemPacket,
)
from mineflex.protocol.packets.play.player import (
    PlayerActionPacket,
    SwingArmPacket,
    UseItemOnPacket,
    UseItemPacket,
)
from mineflex.types import Position, Vec3
from mineflex.world.block import Block

if TYPE_CHECKING:
    from mineflex.bot import Bot


def inject_inventory(bot: Bot) -> None:
    """Inject inventory, slot manipulation, and container handling into bot."""
    bot.inventory = PlayerInventory()
    bot.current_window = None

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
        win: Window
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
            if 36 <= slot_idx <= 44:
                await set_quick_bar_slot(slot_idx - 36)
            else:
                target_slot = bot.inventory.selected_slot
                await click_slot(slot_idx, button=0, mode=0)
                await click_slot(target_slot, button=0, mode=0)

    async def unequip(destination: str = "hand") -> None:
        """Unequip item from specified destination into free inventory space."""
        source_slot = bot.inventory.selected_slot if destination == "hand" else 5
        # Find first empty slot in main inventory (9-35)
        for s in range(9, 36):
            if bot.inventory.get_slot(s) is None:
                await click_slot(source_slot, button=0, mode=0)
                await click_slot(s, button=0, mode=0)
                return

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
        if bot.client and bot.client.is_connected:
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
        if bot.client and bot.client.is_connected:
            await bot.client.send_packet(packet)

    async def toss_stack(item_id: int) -> None:
        """Drop entire item stack."""
        await toss(item_id, count=64)

    async def close_window(window: Optional[Window] = None) -> None:
        """Close active container window."""
        target = window or bot.current_window
        if target:
            if bot.client and bot.client.is_connected:
                await bot.client.send_packet(CloseContainerServerboundPacket(window_id=target.id))
            bot.current_window = None
            bot.emit_sync("window_close", target)

    async def open_block(block: Block) -> Window:
        """Activate a container block and wait for window_open event."""
        open_future: asyncio.Future[Window] = asyncio.get_running_loop().create_future()

        def on_open(win: Window) -> None:
            if not open_future.done():
                open_future.set_result(win)

        bot.once("window_open", on_open)
        await activate_block(block)
        try:
            return await asyncio.wait_for(open_future, timeout=5.0)
        except asyncio.TimeoutError:
            raise InventoryError(f"Timed out waiting for {block.name} window to open")

    async def open_chest(block: Block) -> ChestWindow:
        win = await open_block(block)
        return win  # type: ignore

    async def open_furnace(block: Block) -> FurnaceWindow:
        win = await open_block(block)
        return win  # type: ignore

    async def open_crafting_table(block: Block) -> CraftingTableWindow:
        win = await open_block(block)
        return win  # type: ignore

    async def activate_block(
        block: Block,
        direction: Optional[Union[BlockFace, int, Vec3]] = None,
        cursor_pos: Optional[Vec3] = None,
    ) -> None:
        """Right click / activate a block."""
        if direction is None:
            face = BlockFace.TOP
        elif isinstance(direction, (BlockFace, int)):
            face = BlockFace(direction)
        else:
            face = BlockFace.TOP
        cx = cursor_pos.x if cursor_pos else 0.5
        cy = cursor_pos.y if cursor_pos else 0.5
        cz = cursor_pos.z if cursor_pos else 0.5
        pkt = UseItemOnPacket(
            hand=Hand.MAIN_HAND,
            pos=block.position,
            face=face,
            cursor_x=cx,
            cursor_y=cy,
            cursor_z=cz,
            inside_block=False,
            sequence=0,
        )
        if bot.client and bot.client.is_connected:
            await bot.client.send_packet(pkt)
            await bot.client.send_packet(SwingArmPacket(hand=Hand.MAIN_HAND))

    async def activate_item(hand: str = "main") -> None:
        """Right click / use currently held item."""
        h = Hand.MAIN_HAND if hand == "main" else Hand.OFF_HAND
        if bot.client and bot.client.is_connected:
            await bot.client.send_packet(UseItemPacket(hand=h, sequence=0))

    async def deactivate_item() -> None:
        """Release currently active item (e.g. bow or eating)."""
        if bot.client and bot.client.is_connected:
            await bot.client.send_packet(
                PlayerActionPacket(
                    status=DiggingStatus.RELEASE_USE_ITEM,
                    pos=Position(0, 0, 0),
                    face=0,
                    sequence=0,
                )
            )

    async def consume() -> None:
        """Eat or drink held consumable item (32 ticks / 1.61 seconds)."""
        await activate_item()
        await asyncio.sleep(1.61)
        await deactivate_item()

    async def swing_arm(hand: str = "right") -> None:
        """Swing player arm."""
        h = Hand.MAIN_HAND if hand == "right" else Hand.OFF_HAND
        if bot.client and bot.client.is_connected:
            await bot.client.send_packet(SwingArmPacket(hand=h))

    def recipes_for(
        item_type: Union[int, str],
        metadata: Optional[dict] = None,
        min_result_count: int = 1,
        crafting_table: Optional[Block] = None,
    ) -> List[RecipeDefinition]:
        """Find recipe definitions producing the specified item."""
        matches: List[RecipeDefinition] = []
        target_name = item_type if isinstance(item_type, str) else None
        target_id = item_type if isinstance(item_type, int) else None

        for rec in bot.registry.recipes:
            if rec.result_count < min_result_count:
                continue
            is_3x3 = (
                (len(rec.in_shape) > 2 or any(len(row) > 2 for row in rec.in_shape))
                if rec.in_shape
                else False
            )
            if is_3x3 and crafting_table is None:
                continue
            res_item = bot.registry.items.get(rec.result_item_id)
            if target_name and res_item and res_item.name == target_name:
                matches.append(rec)
            elif target_id is not None and rec.result_item_id == target_id:
                matches.append(rec)
        return matches

    def recipes_all() -> List[RecipeDefinition]:
        """Return all known recipe definitions."""
        return list(bot.registry.recipes)

    async def craft(
        recipe: RecipeDefinition,
        count: int = 1,
        crafting_table: Optional[Block] = None,
    ) -> None:
        """Craft an item according to RecipeDefinition."""
        is_3x3 = (
            (len(recipe.in_shape) > 2 or any(len(row) > 2 for row in recipe.in_shape))
            if recipe.in_shape
            else False
        )
        if is_3x3:
            if crafting_table is None:
                raise CraftingError("Recipe requires a 3x3 crafting table")
            await open_crafting_table(crafting_table)

        for _ in range(count):
            await click_slot(0, button=0, mode=0)

    bot.set_quick_bar_slot = set_quick_bar_slot  # type: ignore
    bot.equip = equip  # type: ignore
    bot.unequip = unequip  # type: ignore
    bot.click_slot = click_slot  # type: ignore
    bot.toss = toss  # type: ignore
    bot.toss_stack = toss_stack  # type: ignore
    bot.close_window = close_window  # type: ignore
    bot.open_chest = open_chest  # type: ignore
    bot.open_furnace = open_furnace  # type: ignore
    bot.open_crafting_table = open_crafting_table  # type: ignore
    bot.activate_block = activate_block  # type: ignore
    bot.activate_item = activate_item  # type: ignore
    bot.deactivate_item = deactivate_item  # type: ignore
    bot.consume = consume  # type: ignore
    bot.swing_arm = swing_arm  # type: ignore
    bot.recipes_for = recipes_for  # type: ignore
    bot.recipes_all = recipes_all  # type: ignore
    bot.craft = craft  # type: ignore
