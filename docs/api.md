# Mineflex API Reference

---

## `create_bot(...) -> Bot`

Creates and initializes a new `Bot` instance.

### Parameters
* `host: str = "localhost"`: Server hostname or IP address.
* `port: int = 25565`: Server port.
* `username: str = "Bot"`: Player username.
* `auth: str = "offline"`: Authentication provider (`"offline"`, `"microsoft"`).
* `version: str = "1.20.1"`: Minecraft protocol target version.
* `keep_alive: bool = True`: Enable automatic KeepAlive responses.
* `timeout: float = 30.0`: Network connection and login timeout in seconds.
* `physics_enabled: bool = True`: Enable 20 Hz movement physics simulation.
* `plugins: Optional[List[PluginType]] = None`: Initial custom plugins to load.

---

## `Bot` Class

Inherits from `AsyncEventEmitter`.

### Properties
* `bot.username: str`: The username of the bot.
* `bot.position: Vec3`: Current 3D position vector in the world.
* `bot.entity: Entity`: The bot's own player entity.
* `bot.entities: dict[int, Entity]`: Dictionary of all currently tracked entities by entity ID.
* `bot.players: dict[str, Player]`: Dictionary of tablist players by username.
* `bot.health: float`: Current health (0.0 to 20.0).
* `bot.food: int`: Current hunger points (0 to 20).
* `bot.food_saturation: float`: Current hunger saturation level.
* `bot.experience: dict`: Experience `{level: int, points: int, progress: float}`.
* `bot.time: int`: World age in ticks.
* `bot.time_of_day: int`: Time of day (0 to 24000).
* `bot.day: int`: In-game days elapsed.
* `bot.game_mode: str`: Game mode (`"survival"`, `"creative"`, `"adventure"`, `"spectator"`).
* `bot.dimension: str`: Current dimension identifier (e.g. `"minecraft:overworld"`).
* `bot.inventory: PlayerInventory`: Player inventory model managing slots 0-45.
* `bot.current_window: Optional[Window]`: Currently open container window, or `None`.
* `bot.world: World`: Loaded world chunk container and block accessor.
* `bot.registry: Registry`: Minecraft data registry for blocks, items, entities, recipes.

### Methods

#### Lifecycle & Network
* `await bot.run() -> None`: Connects to server, authenticates, spawns, and runs main loop.
* `await bot.quit(reason: str = "Quitting") -> None`: Gracefully disconnects and cancels tasks.
* `await bot.end() -> None`: Alias for `quit()`.

#### Communication
* `await bot.chat(message: str) -> None`: Sends a public chat message.
* `await bot.whisper(username: str, message: str) -> None`: Sends a private message via `/tell`.

#### Movement & Physics
* `bot.set_control_state(control: str, state: bool) -> None`: Sets movement controls (`"forward"`, `"back"`, `"left"`, `"right"`, `"jump"`, `"sprint"`, `"sneak"`).
* `bot.clear_control_states() -> None`: Resets all controls to False.
* `await bot.look(yaw: float, pitch: float, force: bool = False) -> None`: Rotates viewing angles.
* `await bot.look_at(target: Vec3, force: bool = False) -> None`: Directs viewing angles toward 3D coordinate.

#### World & Blocks
* `bot.block_at(pos: Vec3 | Position) -> Block`: Returns `Block` at given position.
* `bot.find_blocks(matching, point=None, max_distance=16, count=100) -> list[Vec3]`: Finds block positions.
* `bot.find_block(matching, point=None, max_distance=16) -> Optional[Block]`: Finds nearest block.

#### Actions
* `await bot.dig(block: Block, force_look: bool = True) -> None`: Starts digging block until broken.
* `await bot.stop_digging() -> None`: Cancels ongoing digging operation.
* `await bot.place_block(reference_block: Block, face_vector: Vec3) -> None`: Places held item against block face.
* `await bot.attack(entity: Entity, swing: bool = True) -> None`: Attacks target entity within reach.
* `await bot.mount(entity: Entity) -> None`: Mounts rideable vehicle entity.
* `await bot.dismount() -> None`: Dismounts current vehicle.

#### Inventory
* `await bot.set_quick_bar_slot(slot: int) -> None`: Selects hotbar slot (0 to 8).
* `await bot.equip(item: Item | str | int, destination: str = "hand") -> None`: Equips item.
* `await bot.toss(item_id: int, count: int = 1) -> None`: Drops held item.
* `await bot.click_slot(slot: int, button: int = 0, mode: int = 0) -> None`: Manipulates window slot.

#### Plugins
* `bot.load_plugin(plugin: Plugin | Callable[[Bot], Any]) -> None`: Loads plugin.
* `bot.load_plugins(plugins: list) -> None`: Loads multiple plugins.
* `bot.has_plugin(plugin) -> bool`: Checks if plugin is loaded.

---

## Events

* `connect`: Fired when TCP socket connects.
* `login`: Fired when LoginSuccess is received.
* `spawn`: Fired when bot first spawns and receives world synchronization.
* `chat(username, message, raw_message)`: Fired on player chat.
* `message(chat_component, overlay)`: Fired on all system and action bar messages.
* `health(health, food)`: Fired when health or hunger updates.
* `death`: Fired when bot health reaches 0.
* `block_update(old_block, new_block)`: Fired when a block changes in loaded chunks.
* `entity_spawn(entity)`: Fired when an entity spawns in visual range.
* `entity_moved(entity)`: Fired when a tracked entity moves.
* `entity_gone(entity)`: Fired when an entity despawns or is destroyed.
* `window_open(window)`: Fired when a container window is opened.
* `window_close(window)`: Fired when a container window closes.
* `set_slot(window, slot_idx, item)`: Fired when a slot content updates.
* `physics_tick`: Fired at 20 Hz after every physics simulation step.
* `end(reason)`: Fired when connection closes.
* `error(exc)`: Fired on uncaught errors.
