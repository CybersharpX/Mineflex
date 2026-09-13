# Plugin Architecture in Mineflex

Mineflex is designed from the ground up around a modular, non-monolithic plugin architecture.

---

## Writing a Plugin

Plugins can be created using either a class inheriting from `mineflex.plugins.Plugin` or a simple callable function.

### Class-Based Plugin

```python
from mineflex import Bot
from mineflex.plugins import Plugin


class AutoEatPlugin(Plugin):
    name = "auto_eat"

    def setup(self, bot: Bot) -> None:
        @bot.on("health")
        async def on_health(health, food):
            if food < 14:
                food_item = bot.inventory.find_inventory_item("bread")
                if food_item:
                    await bot.equip(food_item)
                    # Use food item
                    await bot.chat("Eating bread to replenish hunger...")
```

### Callable Function Plugin

```python
def logger_plugin(bot):
    @bot.on("chat")
    def on_chat(username, message, *args):
        print(f"[Log] {username}: {message}")
```

---

## Loading Plugins

Load plugins on the bot instance using `load_plugin`:

```python
bot = create_bot(...)
bot.load_plugin(AutoEatPlugin())
bot.load_plugin(logger_plugin)
```
