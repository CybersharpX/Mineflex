"""Window and PlayerInventory management."""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple, Union

from mineflex.inventory.item import Item
from mineflex.inventory.slot import Slot


class Window:
    """Base class for Minecraft container windows."""

    def __init__(
        self, window_id: int, title: str = "Window", window_type: int = 0, slot_count: int = 46
    ) -> None:
        self.id = window_id
        self.title = title
        self.type = window_type
        self.slots: Dict[int, Slot] = {i: Slot(i) for i in range(slot_count)}
        self.carried_item: Optional[Item] = None

    def get_slot(self, index: int) -> Optional[Item]:
        slot = self.slots.get(index)
        return slot.item if slot else None

    def set_slot(self, index: int, item: Optional[Item]) -> None:
        if index not in self.slots:
            self.slots[index] = Slot(index)
        self.slots[index].item = item

    def first_empty_slot(
        self, start_slot: int = 0, end_slot: Optional[int] = None
    ) -> Optional[int]:
        max_s = end_slot if end_slot is not None else len(self.slots)
        for i in range(start_slot, max_s):
            slot = self.slots.get(i)
            if slot is None or slot.is_empty:
                return i
        return None

    def find_items(self, name_or_id: Union[str, int]) -> List[Tuple[int, Item]]:
        """Find all slots containing the matching item."""
        matches: List[Tuple[int, Item]] = []
        for idx, slot in self.slots.items():
            if slot.item is not None:
                if isinstance(name_or_id, str) and slot.item.name == name_or_id:
                    matches.append((idx, slot.item))
                elif isinstance(name_or_id, int) and slot.item.id == name_or_id:
                    matches.append((idx, slot.item))
        return matches

    def find_item(self, name_or_id: Union[str, int]) -> Optional[Item]:
        """Find the first matching item in this window."""
        items = self.find_items(name_or_id)
        return items[0][1] if items else None

    def count(self, name_or_id: Union[str, int]) -> int:
        """Count total items of matching name or id in this window."""
        return sum(item.count for _, item in self.find_items(name_or_id))

    def clear(self) -> None:
        for slot in self.slots.values():
            slot.clear()
        self.carried_item = None


class PlayerInventory(Window):
    """Player inventory window (window ID 0) managing 46 slots."""

    CRAFT_OUTPUT_SLOT = 0
    CRAFT_GRID_START = 1
    CRAFT_GRID_END = 5
    ARMOR_START = 5
    ARMOR_END = 9
    MAIN_START = 9
    MAIN_END = 36
    HOTBAR_START = 36
    HOTBAR_END = 45
    OFFHAND_SLOT = 45

    def __init__(self) -> None:
        super().__init__(window_id=0, title="Inventory", slot_count=46)
        self.selected_hotbar_slot: int = 0  # 0 to 8

    @property
    def selected_slot(self) -> int:
        """Absolute slot index of the currently selected hotbar item (36 to 44)."""
        return self.HOTBAR_START + self.selected_hotbar_slot

    @property
    def selected_item(self) -> Optional[Item]:
        """The item currently held in the player's main hand."""
        return self.get_slot(self.selected_slot)

    def set_selected_slot(self, slot_idx: int) -> None:
        if 0 <= slot_idx <= 8:
            self.selected_hotbar_slot = slot_idx
        else:
            raise ValueError(f"Hotbar slot must be between 0 and 8, got {slot_idx}")

    @property
    def head(self) -> Optional[Item]:
        return self.get_slot(5)

    @property
    def torso(self) -> Optional[Item]:
        return self.get_slot(6)

    @property
    def legs(self) -> Optional[Item]:
        return self.get_slot(7)

    @property
    def feet(self) -> Optional[Item]:
        return self.get_slot(8)

    @property
    def off_hand(self) -> Optional[Item]:
        return self.get_slot(self.OFFHAND_SLOT)

    def find_inventory_item(self, name_or_id: Union[str, int]) -> Optional[Item]:
        """Find matching item specifically in main inventory or hotbar (slots 9-44)."""
        for idx in range(self.MAIN_START, self.HOTBAR_END):
            item = self.get_slot(idx)
            if item is not None:
                if isinstance(name_or_id, str) and item.name == name_or_id:
                    return item
                elif isinstance(name_or_id, int) and item.id == name_or_id:
                    return item
        return None
