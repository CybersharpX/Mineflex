"""Inventory slot representation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from mineflex.inventory.item import Item


@dataclass
class Slot:
    """Represents a specific slot within a container window."""

    index: int
    item: Optional[Item] = None

    @property
    def is_empty(self) -> bool:
        return self.item is None or self.item.count <= 0

    def clear(self) -> None:
        self.item = None

    def __repr__(self) -> str:
        return f"Slot(index={self.index}, item={self.item})"
