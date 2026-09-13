"""Unit tests for Minecraft Data and Registries."""

from mineflex.data import Registry


def test_registry_blocks():
    reg = Registry("1.20.1")

    # Look up by ID and name
    stone_by_name = reg.blocks_by_name["stone"]
    stone_by_id = reg.blocks[1]
    assert stone_by_name == stone_by_id
    assert stone_by_name.name == "stone"
    assert stone_by_name.hardness == 1.5
    assert stone_by_name.diggable is True
    assert stone_by_name.is_air is False
    assert stone_by_name.solid is True

    # Look up air
    air = reg.blocks_by_name["air"]
    assert air.is_air is True
    assert air.solid is False

    # Look up by state id
    block_from_state = reg.get_block_by_state_id(15)  # oak_planks
    assert block_from_state.name == "oak_planks"


def test_registry_items():
    reg = Registry("1.20.1")
    diamond_sword = reg.items_by_name["diamond_sword"]
    assert diamond_sword.id == 612
    assert diamond_sword.stack_size == 1

    stick = reg.items_by_name["stick"]
    assert stick.stack_size == 64


def test_registry_entities():
    reg = Registry("1.20.1")
    player = reg.entities_by_name["player"]
    assert player.width == 0.6
    assert player.height == 1.8

    zombie = reg.entities_by_name["zombie"]
    assert zombie.category == "hostile"


def test_registry_recipes():
    reg = Registry("1.20.1")
    stick_recipes = [r for r in reg.recipes if r.name == "stick"]
    assert len(stick_recipes) == 1
    assert stick_recipes[0].result_count == 4
