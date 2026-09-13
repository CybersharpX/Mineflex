# Compatibility Matrix: Mineflayer vs Mineflex

This matrix provides a detailed, verified status comparison across all 50 fundamental features between PrismarineJS Mineflayer and Mineflex.

---

| # | Mineflayer Feature | Mineflex Equivalent | Implementation Status | Test Suite |
|---|---|---|---|---|
| 1 | `createBot` entrypoint | `mineflex.create_bot` | **Verified** | `tests/test_bot.py` |
| 2 | `bot.run` lifecycle | `await bot.run()` | **Verified** | `integration_tests/test_integration.py` |
| 3 | `bot.quit` / `bot.end` | `await bot.quit()` | **Verified** | `tests/test_bot.py` |
| 4 | Event System (`on`, `emit`) | `AsyncEventEmitter` | **Verified** | `tests/test_events.py` |
| 5 | Chat sending | `await bot.chat(...)` | **Verified** | `integration_tests/test_integration.py` |
| 6 | Chat receiving & parsing | `bot.on("chat")` | **Verified** | `tests/test_chat.py` |
| 7 | Custom chat patterns | `bot.add_chat_pattern` | **Verified** | `tests/test_chat.py` |
| 8 | Await message | `await bot.await_message` | **Verified** | `tests/test_chat.py` |
| 9 | Entity tracking | `EntityTracker` | **Verified** | `tests/test_entities.py` |
| 10 | Nearest entity search | `bot.nearest_entity` | **Verified** | `tests/test_entities.py` |
| 11 | Entity at cursor (Ray-AABB) | `bot.entity_at_cursor` | **Verified** | `tests/test_entities.py` |
| 12 | Block lookup | `bot.block_at` | **Verified** | `tests/test_world.py` |
| 13 | Block searching | `bot.find_blocks` | **Verified** | `tests/test_world.py` |
| 14 | Amanatides-Woo Raycasting | `world.raycast` | **Verified** | `tests/test_world.py` |
| 15 | Block at cursor | `bot.block_at_cursor` | **Verified** | `tests/test_world.py` |
| 16 | Block line of sight | `bot.can_see_block` | **Verified** | `tests/test_world.py` |
| 17 | Paletted chunk storage | `Chunk`, `ChunkSection` | **Verified** | `tests/test_world.py` |
| 18 | Chunk lifecycle & unload | `world.unload_chunk` | **Verified** | `tests/test_world.py` |
| 19 | 20 Hz deterministic physics | `PhysicsEngine` | **Verified** | `tests/test_physics.py` |
| 20 | Movement controls | `bot.set_control_state` | **Verified** | `tests/test_physics.py` |
| 21 | Liquid physics & buoyancy | `engine._apply_fluid_forces` | **Verified** | `tests/test_physics.py` |
| 22 | Ladder & vine climbing | `engine._apply_climbing` | **Verified** | `tests/test_physics.py` |
| 23 | Sneaking ledge containment | `engine._contain_on_ledge` | **Verified** | `tests/test_physics.py` |
| 24 | Knockback impulses | `engine.apply_knockback` | **Verified** | `tests/test_physics.py` |
| 25 | Look direction & lookAt | `await bot.look_at(...)` | **Verified** | `tests/test_physics.py` |
| 26 | Wait for simulation ticks | `await bot.wait_for_ticks` | **Verified** | `tests/test_physics.py` |
| 27 | 46-slot player inventory | `PlayerInventory` | **Verified** | `tests/test_inventory.py` |
| 28 | Hotbar slot selection | `await bot.set_quick_bar_slot`| **Verified** | `tests/test_inventory.py` |
| 29 | Equipping / unequipping | `await bot.equip` | **Verified** | `tests/test_inventory.py` |
| 30 | Tossing items | `await bot.toss` | **Verified** | `tests/test_inventory.py` |
| 31 | Tossing full stacks | `await bot.toss_stack` | **Verified** | `tests/test_inventory.py` |
| 32 | Container window tracking | `ChestWindow`, `Window` | **Verified** | `tests/test_inventory.py` |
| 33 | Open chest window | `await bot.open_chest` | **Verified** | `tests/test_inventory.py` |
| 34 | Open furnace window | `await bot.open_furnace` | **Verified** | `tests/test_inventory.py` |
| 35 | Open crafting table | `await bot.open_crafting_table`| **Verified** | `tests/test_inventory.py` |
| 36 | Close window | `await bot.close_window` | **Verified** | `tests/test_inventory.py` |
| 37 | Recipe search | `bot.recipes_for`, `recipes_all` | **Verified** | `tests/test_data.py` |
| 38 | Crafting automation | `await bot.craft` | **Verified** | `tests/test_inventory.py` |
| 39 | Block interaction / activation | `await bot.activate_block` | **Verified** | `tests/test_inventory.py` |
| 40 | Item activation & deactivation | `activate_item`, `deactivate_item` | **Verified** | `tests/test_inventory.py` |
| 41 | Item consumption | `await bot.consume` | **Verified** | `tests/test_inventory.py` |
| 42 | Arm swing animation | `await bot.swing_arm` | **Verified** | `tests/test_inventory.py` |
| 43 | Dig duration calculation | `bot.dig_time` | **Verified** | `tests/test_world.py` |
| 44 | Block digging & cancellation | `bot.dig`, `bot.stop_digging` | **Verified** | `integration_tests/test_integration.py` |
| 45 | Block placement | `await bot.place_block` | **Verified** | `integration_tests/test_integration.py` |
| 46 | Combat attack & reach | `await bot.attack` | **Verified** | `integration_tests/test_integration.py` |
| 47 | Vehicle mount & dismount | `bot.mount`, `bot.dismount` | **Verified** | `tests/test_bot.py` |
| 48 | Protocol 1.20.2+ Configuration | `mineflex.protocol.packets.configuration` | **Verified** | `tests/test_protocol.py` |
| 49 | AES-128-CFB8 Decrypting stream | `DecryptingStreamReader` | **Verified** | `tests/test_protocol.py` |
| 50 | Stream fuzzing & soak stability | `test_protocol_robustness`, `test_soak` | **Verified** | `integration_tests/test_soak.py` |
