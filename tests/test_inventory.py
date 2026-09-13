"""Unit tests for inventory, slots, windows, and containers."""

from mineflex.inventory import ChestWindow, Item, PlayerInventory


def test_player_inventory_slots():
    inv = PlayerInventory()
    assert len(inv.slots) == 46
    assert inv.selected_slot == 36  # slot 0 of hotbar is 36

    inv.set_selected_slot(4)
    assert inv.selected_slot == 40

    # Put a sword in hotbar slot 4 (slot 40)
    sword = Item(id=612, name="diamond_sword", count=1)
    inv.set_slot(40, sword)

    assert inv.selected_item == sword
    assert inv.find_inventory_item("diamond_sword") == sword


def test_inventory_counting_and_finding():
    inv = PlayerInventory()
    inv.set_slot(36, Item(id=600, name="stick", count=32))
    inv.set_slot(37, Item(id=600, name="stick", count=16))

    assert inv.count("stick") == 48
    sticks = inv.find_items("stick")
    assert len(sticks) == 2
    assert sticks[0][0] == 36
    assert sticks[1][0] == 37


def test_chest_window():
    chest = ChestWindow(window_id=1, title="Large Chest", double=True)
    assert chest.chest_slots == 54
    assert len(chest.slots) == 54 + 36

    apple = Item(id=620, name="apple", count=10)
    chest.set_slot(0, apple)
    assert chest.get_slot(0) == apple
    assert chest.count("apple") == 10
