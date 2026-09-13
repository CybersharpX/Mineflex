"""Item and ItemStack model."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from mineflex.data.provider import Registry
from mineflex.nbt.tags import TagCompound


@dataclass
class Item:
    """Represents an ItemStack with ID, count, and optional NBT components."""

    id: int
    count: int = 1
    name: str = "item"
    display_name: str = "Item"
    stack_size: int = 64
    nbt: Optional[TagCompound] = None

    @classmethod
    def from_slot(cls, slot_dict: dict[str, Any], registry: Optional[Registry] = None) -> Item:
        reg = registry or Registry("1.20.1")
        item_id = slot_dict["id"]
        i_def = reg.items.get(item_id)
        name = i_def.name if i_def else f"item_{item_id}"
        display_name = i_def.display_name if i_def else name
        stack_size = i_def.stack_size if i_def else 64
        return cls(
            id=item_id,
            count=slot_dict.get("count", 1),
            name=name,
            display_name=display_name,
            stack_size=stack_size,
            nbt=slot_dict.get("nbt"),
        )

    def to_slot(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "count": self.count,
            "nbt": self.nbt,
        }

    def clone(self) -> Item:
        return Item(
            id=self.id,
            count=self.count,
            name=self.name,
            display_name=self.display_name,
            stack_size=self.stack_size,
            nbt=self.nbt,
        )

    def __repr__(self) -> str:
        return f"Item({self.name} x{self.count})"
