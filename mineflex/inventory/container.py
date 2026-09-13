"""Specialized container window models (Chest, Furnace, Crafting Table)."""

from __future__ import annotations

from mineflex.inventory.window import Window


class ChestWindow(Window):
    """Chest container window (single 27 slots or double 54 slots + 36 player slots)."""

    def __init__(self, window_id: int, title: str = "Chest", double: bool = False) -> None:
        chest_slots = 54 if double else 27
        total_slots = chest_slots + 36  # Chest slots + player inventory slots
        super().__init__(window_id=window_id, title=title, window_type=0, slot_count=total_slots)
        self.chest_slots = chest_slots


class CraftingTableWindow(Window):
    """Crafting Table 3x3 window (1 result slot, 9 grid slots + 36 player slots)."""

    def __init__(self, window_id: int, title: str = "Crafting") -> None:
        super().__init__(window_id=window_id, title=title, window_type=11, slot_count=46)


class FurnaceWindow(Window):
    """Furnace window (3 slots + 36 player slots)."""

    def __init__(self, window_id: int, title: str = "Furnace") -> None:
        super().__init__(window_id=window_id, title=title, window_type=13, slot_count=39)
