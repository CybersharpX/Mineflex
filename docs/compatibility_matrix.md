# Compatibility Matrix: Mineflayer vs Mineflex

This matrix provides a detailed, honest status comparison between PrismarineJS Mineflayer and Mineflex.

---

| Mineflayer Feature | Mineflex Equivalent | Status | Tests | Notes |
|---|---|---|---|---|
| `createBot` | `mineflex.create_bot` | Implemented | Yes | Supports host, port, username, auth, version, physics_enabled. |
| `bot.run` / loop | `await bot.run()` | Implemented | Yes | Asyncio event-loop native lifecycle. |
| `bot.quit` / `bot.end` | `await bot.quit()` / `await bot.end()` | Implemented | Yes | Cleanly tears down tasks and closes TCP sockets. |
| Event System (`on`, `once`, `off`, `emit`) | `AsyncEventEmitter` | Implemented | Yes | Fully supports async and sync handlers with safe exception isolation. |
| Chat sending (`bot.chat`, `bot.whisper`) | `await bot.chat(...)` | Implemented | Yes | Sends serverbound ChatMessage packets; verified via integration test. |
| Chat receiving (`chat`, `message` events) | `bot.on("chat")` | Implemented | Yes | Parses JSON components, colors, and legacy formatting. |
| Entity tracking (`bot.entities`, `bot.players`) | `EntityTracker` | Implemented | Yes | Tracks spawn, movement deltas, rotation, velocity, and despawn. |
| Spatial entity queries (`bot.nearestEntity`) | `bot.nearest_entity(...)` | Implemented | Yes | Filter predicate supported with euclidean distance evaluation. |
| Block queries (`bot.blockAt`) | `bot.block_at(...)` | Implemented | Yes | Returns rich `Block` with hardness, solid, bounding box properties. |
| Block searching (`bot.findBlocks`, `bot.findBlock`) | `bot.find_blocks`, `bot.find_block` | Implemented | Yes | Finds nearest blocks within radius by name, id, or predicate. |
| World chunk storage | `World`, `Chunk`, `ChunkSection` | Implemented | Yes | 1.20+ paletted bit array decompression (single-value, indirect, direct). |
| Physics simulation | `PhysicsEngine` | Implemented | Yes | Deterministic 20 Hz simulation: gravity, friction, jumping, stepping, AABB collision. |
| Movement controls (`bot.setControlState`) | `bot.set_control_state(...)` | Implemented | Yes | Controls: `forward`, `back`, `left`, `right`, `jump`, `sprint`, `sneak`. |
| Look direction (`bot.look`, `bot.lookAt`) | `await bot.look(...)`, `await bot.look_at(...)` | Implemented | Yes | Pitch and yaw trigonometry and network packet dispatch. |
| Inventory slots (`bot.inventory`) | `PlayerInventory` | Implemented | Yes | Full 46 slots model: crafting, armor, main inventory, hotbar, offhand. |
| Hotbar selection (`bot.setQuickBarSlot`) | `await bot.set_quick_bar_slot(...)` | Implemented | Yes | Dispatches SetHeldItem packet. |
| Item equipping (`bot.equip`) | `await bot.equip(...)` | Implemented | Yes | Equips from inventory to hand or destination. |
| Item dropping (`bot.toss`) | `await bot.toss(...)` | Implemented | Yes | Sends PlayerAction drop packet. |
| Container windows (`bot.openContainer`) | `ChestWindow`, `CraftingTableWindow` | Implemented | Yes | Supports 27/54 chest slots, crafting grids, and window click packets. |
| Block digging (`bot.dig`, `bot.stopDigging`) | `await bot.dig(...)`, `await bot.stop_digging()` | Implemented | Yes | Calculates hardness/tool duration; sends start/finish digging packets. |
| Block placement (`bot.placeBlock`) | `await bot.place_block(...)` | Implemented | Yes | Face calculation, cursor coordinates, and UseItemOn packet. |
| Combat attack (`bot.attack`) | `await bot.attack(...)` | Implemented | Yes | Validates 4.5 block reach; sends Interact packet and swing arm. |
| Vehicle mounting (`bot.mount`, `bot.dismount`) | `await bot.mount(...)`, `await bot.dismount()` | Implemented | Yes | Interacts with entity; dismounts via sneak. |
| Plugin System (`bot.loadPlugin`) | `bot.load_plugin(...)` | Implemented | Yes | Supports class-based plugins and callable functions. |
| Offline Authentication | `OfflineAuthProvider` | Implemented | Yes | Vanilla-compatible deterministic UUID v3 algorithm. |
| Microsoft Authentication | `MicrosoftAuthProvider` | Partial | Yes | Token-based session authentication stub. |
| Protocol Encryption (AES-128 CFB8) | `EncryptionCipher` | Implemented | Yes | Full stream cipher using cryptography. |
| Protocol Compression (zlib) | `PacketFramer` | Implemented | Yes | Compression threshold negotiation and streaming zlib decompression. |
| NBT Parser & Serializer | `mineflex.nbt` | Implemented | Yes | All 12 tag types, compounds, lists, network mode, and byte arrays. |
