# Mineflex Current State & Audit Baseline

## 1. Project Overview

Mineflex is a production-grade, 100% native Python implementation inspired by and behaviorally compatible with PrismarineJS Mineflayer. It operates asynchronously via standard `asyncio`, contains zero Node.js bridges or subprocess wrappers, and enforces strict static typing (mypy compliant, `py.typed` marker).

---

## 2. Codebase Metrics

| Metric | Measurement |
|---|---|
| **Total Source Files** | 74 Python modules (`mineflex/`) |
| **Total Lines of Source Code** | ~7,800+ lines |
| **Total Automated Tests** | 75 tests across unit, fuzz, and integration suites |
| **Test Pass Rate** | **100% (75/75 passed)** |
| **Overall Code Coverage** | **79%** across all 74 modules |
| **Type Check Status** | **0 errors** (`python -m mypy mineflex` across all 74 files) |
| **Linter Status** | **0 warnings / 0 errors** (`python -m ruff check .`) |
| **Package Distribution** | Builds cleanly (`.whl` and `.tar.gz`) with bundled registries |

---

## 3. Subsystem Status Breakdown

### Protocol & Networking
- **Connection Pipeline**: Implements `ClientConnection` over `asyncio.StreamReader` / `asyncio.StreamWriter`.
- **Encryption**: AES-128-CFB8 symmetric stream cipher implemented using Python `cryptography` primitives. `DecryptingStreamReader` wraps the incoming stream for transparent on-the-fly decryption prior to VarInt frame decoding.
- **Framing & Compression**: Dynamic `PacketFramer` supporting uncompressed negotiation and zlib stream decompression according to server-negotiated thresholds.
- **Protocol States**: Full support for `HANDSHAKING (0)`, `STATUS (1)`, `LOGIN (2)`, `PLAY (3)`, and `CONFIGURATION (4)`.
- **Packet Codec Registry**: `ProtocolRegistry` tracks 56 registered strongly typed packet codecs across protocol versions 763 (1.20.1) and 764 (1.20.2+). Zero packet ID collisions detected.
- **Configuration State Handling**: Automated bidirectional acknowledgment of KeepAlive, FeatureFlags, KnownPacks, RegistryData, and FinishConfiguration packets.

### Physics Simulation
- **Simulation Loop**: Fixed-step 20 Hz (50 ms) deterministic physics engine replicating vanilla player kinematics.
- **Movement Physics**: Gravity, terminal velocity, ground friction, air resistance, jump impulses, step-up assistance (0.6 blocks), and knockback impulses.
- **Fluids & Buoyancy**: Fluid drag, sinking, and buoyancy for both water and lava.
- **Climbing**: Ladder and vine ascension/descension with vertical speed clamping.
- **Ledge Containment**: Sneaking / crouching edge containment preventing accidental falls off blocks.
- **Collisions**: 3D Axis-Aligned Bounding Box (AABB) intersection and broadphase queries against paletted world blocks.

### World Representation & Spatial Queries
- **Paletted Storage**: 16x16x16 `ChunkSection` paletted storage supporting single-value, indirect palette (4-8 bits/block), and direct global palette (>8 bits/block) with bit-unpacking across 64-bit integers.
- **Raycasting**: Amanatides-Woo 3D grid traversal algorithm (`world.raycast`) for precise voxel intersection up to specified reach distances.
- **Sight Checks**: `bot.block_at_cursor`, `bot.block_in_sight`, and `bot.can_see_block` with eye-position line-of-sight obstruction checking.
- **Chunk Lifecycle**: Chunk loading from packet data, block updates, chunk unloading (`unload_chunk`), and world resets.

### Inventory, Crafting & Actions
- **Inventory Model**: Vanilla 46-slot player inventory covering crafting 2x2, armor, main inventory (27 slots), hotbar (9 slots), and offhand.
- **Container Windows**: Chest (single 27-slot and double 54-slot), furnace, and 3x3 crafting table windows.
- **Window Operations**: Window clicks, slot picking, quick-bar slot selection, tossing items/stacks, equipping/unequipping.
- **Interactions**: Activating blocks (`activate_block`), item consumption (`consume`), right-click activation/deactivation (`activate_item`, `deactivate_item`), arm swinging (`swing_arm`).
- **Crafting Engine**: Recipe lookup (`recipes_for`, `recipes_all`) and crafting table automation (`craft`).
- **Digging & Building**: Hardness-based dig time calculation (`dig_time`), reach validation (`can_dig_block`), start/cancel/finish digging packets, block placement against adjacent block faces.

### Entity System
- **Tracking**: Entity spawns, UUID tracking, position deltas, absolute position updates, head yaw / pitch rotation, velocity impulses, and despawn handling.
- **Spatial Queries**: `bot.nearest_entity` with filter predicates and `bot.entity_at_cursor` utilizing ray-AABB geometric intersection tests.

### Chat & Messaging
- **Component Parser**: Parses modern JSON chat components, legacy section-sign `§` color formatting, hover/click events, and plain text.
- **Pattern Matching**: Regex pattern registration (`add_chat_pattern`), group capture dispatch (`chat:<name>`), and async message waiting (`await_message`).
