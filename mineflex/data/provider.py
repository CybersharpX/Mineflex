"""Minecraft data registries and domain models."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass(frozen=True)
class BlockDefinition:
    """Definition of a Minecraft block type."""

    id: int
    name: str
    hardness: float = 1.0
    diggable: bool = True
    transparent: bool = False
    solid: bool = True
    bounding_box: str = "block"  # "block", "empty", or custom
    material: str = "default"
    harvest_tools: tuple[str, ...] = ()
    default_state_id: int = 0
    min_state_id: int = 0
    max_state_id: int = 0

    @property
    def is_air(self) -> bool:
        return "air" in self.name

    @property
    def is_liquid(self) -> bool:
        return self.name in ("water", "lava")


@dataclass(frozen=True)
class ItemDefinition:
    """Definition of a Minecraft item type."""

    id: int
    name: str
    display_name: str
    stack_size: int = 64


@dataclass(frozen=True)
class EntityDefinition:
    """Definition of a Minecraft entity type."""

    id: int
    name: str
    category: str = "unknown"
    width: float = 0.6
    height: float = 1.8


@dataclass(frozen=True)
class BiomeDefinition:
    """Definition of a Minecraft biome."""

    id: int
    name: str
    category: str = "none"
    temperature: float = 0.5


@dataclass(frozen=True)
class RecipeDefinition:
    """Definition of a crafting recipe."""

    name: str
    result_item_id: int
    result_count: int = 1
    in_shape: Optional[tuple[tuple[Optional[int], ...], ...]] = None
    ingredients: tuple[int, ...] = ()


class Registry:
    """Central registry for Minecraft blocks, items, entities, biomes, and recipes."""

    def __init__(self, version: str = "1.20.1") -> None:
        self.version = version
        self.blocks: Dict[int, BlockDefinition] = {}
        self.blocks_by_name: Dict[str, BlockDefinition] = {}
        self.blocks_by_state_id: Dict[int, BlockDefinition] = {}
        self.items: Dict[int, ItemDefinition] = {}
        self.items_by_name: Dict[str, ItemDefinition] = {}
        self.entities: Dict[int, EntityDefinition] = {}
        self.entities_by_name: Dict[str, EntityDefinition] = {}
        self.biomes: Dict[int, BiomeDefinition] = {}
        self.biomes_by_name: Dict[str, BiomeDefinition] = {}
        self.recipes: List[RecipeDefinition] = []

        self._load_standard_data()

    def _load_standard_data(self) -> None:
        registry_dir = Path(__file__).parent / "registries"
        blocks_file = registry_dir / "blocks.json"
        items_file = registry_dir / "items.json"
        entities_file = registry_dir / "entities.json"
        biomes_file = registry_dir / "biomes.json"
        recipes_file = registry_dir / "recipes.json"

        if blocks_file.exists():
            with open(blocks_file, "r", encoding="utf-8") as f:
                raw_blocks = json.load(f)
                for b in raw_blocks:
                    b_def = BlockDefinition(
                        id=b["id"],
                        name=b["name"],
                        hardness=b.get("hardness", 1.0),
                        diggable=b.get("diggable", True),
                        transparent=b.get("transparent", False),
                        solid=b.get("solid", True),
                        bounding_box=b.get("bounding_box", "block"),
                        material=b.get("material", "default"),
                        harvest_tools=tuple(b.get("harvest_tools", ())),
                        default_state_id=b.get("default_state_id", b["id"]),
                        min_state_id=b.get("min_state_id", b.get("default_state_id", b["id"])),
                        max_state_id=b.get("max_state_id", b.get("default_state_id", b["id"])),
                    )
                    self.blocks[b_def.id] = b_def
                    self.blocks_by_name[b_def.name] = b_def
                    for sid in range(b_def.min_state_id, b_def.max_state_id + 1):
                        self.blocks_by_state_id[sid] = b_def

        if items_file.exists():
            with open(items_file, "r", encoding="utf-8") as f:
                raw_items = json.load(f)
                for i in raw_items:
                    i_def = ItemDefinition(
                        id=i["id"],
                        name=i["name"],
                        display_name=i.get("display_name", i["name"]),
                        stack_size=i.get("stack_size", 64),
                    )
                    self.items[i_def.id] = i_def
                    self.items_by_name[i_def.name] = i_def

        if entities_file.exists():
            with open(entities_file, "r", encoding="utf-8") as f:
                raw_entities = json.load(f)
                for e in raw_entities:
                    e_def = EntityDefinition(
                        id=e["id"],
                        name=e["name"],
                        category=e.get("category", "unknown"),
                        width=e.get("width", 0.6),
                        height=e.get("height", 1.8),
                    )
                    self.entities[e_def.id] = e_def
                    self.entities_by_name[e_def.name] = e_def

        if biomes_file.exists():
            with open(biomes_file, "r", encoding="utf-8") as f:
                raw_biomes = json.load(f)
                for bio in raw_biomes:
                    bio_def = BiomeDefinition(
                        id=bio["id"],
                        name=bio["name"],
                        category=bio.get("category", "none"),
                        temperature=bio.get("temperature", 0.5),
                    )
                    self.biomes[bio_def.id] = bio_def
                    self.biomes_by_name[bio_def.name] = bio_def

        if recipes_file.exists():
            with open(recipes_file, "r", encoding="utf-8") as f:
                raw_recipes = json.load(f)
                for r in raw_recipes:
                    self.recipes.append(
                        RecipeDefinition(
                            name=r.get("name", "recipe"),
                            result_item_id=r["result"]["id"],
                            result_count=r["result"].get("count", 1),
                            ingredients=tuple(r.get("ingredients", ())),
                        )
                    )

    def get_block_by_state_id(self, state_id: int) -> Optional[BlockDefinition]:
        """Get BlockDefinition by state ID, defaulting to air if unknown."""
        return self.blocks_by_state_id.get(state_id) or self.blocks_by_name.get("air")
