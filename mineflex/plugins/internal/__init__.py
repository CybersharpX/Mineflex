"""Internal core plugins for Mineflex."""

from __future__ import annotations

from mineflex.plugins.internal.actions import inject_actions
from mineflex.plugins.internal.blocks import inject_blocks
from mineflex.plugins.internal.chat import inject_chat
from mineflex.plugins.internal.entities import inject_entities
from mineflex.plugins.internal.game import inject_game, inject_health, inject_time
from mineflex.plugins.internal.inventory import inject_inventory
from mineflex.plugins.internal.physics import inject_physics

STANDARD_INTERNAL_PLUGINS = [
    inject_game,
    inject_health,
    inject_time,
    inject_blocks,
    inject_entities,
    inject_physics,
    inject_inventory,
    inject_actions,
    inject_chat,
]

__all__ = ["STANDARD_INTERNAL_PLUGINS"]
