"""Block representation for world queries and physics collision."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional

from mineflex.data.provider import BlockDefinition
from mineflex.types import AABB, Vec3


@dataclass
class Block:
    """Rich block instance in the world with spatial coordinates and physical properties."""

    position: Vec3
    state_id: int
    definition: BlockDefinition
    metadata: Optional[dict] = None

    @property
    def name(self) -> str:
        return self.definition.name

    @property
    def id(self) -> int:
        return self.definition.id

    @property
    def hardness(self) -> float:
        return self.definition.hardness

    @property
    def diggable(self) -> bool:
        return self.definition.diggable

    @property
    def transparent(self) -> bool:
        return self.definition.transparent

    @property
    def solid(self) -> bool:
        return self.definition.solid

    @property
    def is_air(self) -> bool:
        return self.definition.is_air

    @property
    def is_liquid(self) -> bool:
        return self.definition.is_liquid

    @property
    def bounding_box(self) -> str:
        return self.definition.bounding_box

    def get_collision_shapes(self) -> List[AABB]:
        """Get the world-space bounding boxes for this block."""
        if not self.solid or self.bounding_box == "empty" or self.is_air:
            return []
        # Standard full solid block
        bx = math.floor(self.position.x)
        by = math.floor(self.position.y)
        bz = math.floor(self.position.z)
        return [AABB(bx, by, bz, bx + 1.0, by + 1.0, bz + 1.0)]

    def __repr__(self) -> str:
        return f"Block({self.name}, pos={self.position.floored()}, state={self.state_id})"
