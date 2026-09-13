"""Tooling script to regenerate or inspect Minecraft data registries.

DO NOT EDIT MANUALLY GENERATED DATA DIRECTLY.
"""

from __future__ import annotations

from mineflex.data.provider import Registry


def verify_registries() -> None:
    registry = Registry("1.20.1")
    print(
        f"Loaded {len(registry.blocks)} blocks, {len(registry.items)} items, "
        f"{len(registry.entities)} entities, {len(registry.biomes)} biomes, "
        f"{len(registry.recipes)} recipes."
    )


if __name__ == "__main__":
    verify_registries()
