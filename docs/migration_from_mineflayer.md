# Migration from Mineflayer to Mineflex

Mineflex is designed so that developers familiar with PrismarineJS's Mineflayer can immediately understand and write Python bots using identical conceptual patterns.

---

## Direct Conceptual Mapping

| Mineflayer Concept (JavaScript) | Mineflex Concept (Python) | Notes |
|---|---|---|
| `mineflayer.createBot(options)` | `mineflex.create_bot(**kwargs)` | Standard Python kwargs |
| `bot.on('event', callback)` | `@bot.on("event")` or `bot.on("event", fn)` | Async and sync functions supported |
| `bot.once('event', callback)` | `@bot.once("event")` | One-shot execution |
| `bot.chat(message)` | `await bot.chat(message)` | Awaitable asyncio coroutine |
| `bot.entity.position` | `bot.entity.position` / `bot.position` | Rich `Vec3` object with arithmetic |
| `bot.blockAt(vec)` | `bot.block_at(vec)` | PEP-8 snake_case method naming |
| `bot.nearestEntity(filter)` | `bot.nearest_entity(filter)` | Callable predicate supported |
| `bot.dig(block)` | `await bot.dig(block)` | Awaitable; supports cancellation |
| `bot.attack(entity)` | `await bot.attack(entity)` | Validates reach distance |
| `bot.inventory.items()` | `bot.inventory.slots` | Typed `Item` models |
| `bot.loadPlugin(plugin)` | `bot.load_plugin(plugin)` | Class or callable supported |

---

## Code Comparison Example

### Mineflayer (JavaScript)

```javascript
const mineflayer = require('mineflayer')

const bot = mineflayer.createBot({
  host: 'localhost',
  username: 'Bot'
})

bot.on('chat', (username, message) => {
  if (username === bot.username) return
  bot.chat(`You said: ${message}`)
})
```

### Mineflex (Python)

```python
import asyncio
from mineflex import create_bot


async def main():
    bot = create_bot(host="localhost", username="Bot")

    @bot.on("chat")
    async def on_chat(username, message, *args):
        if username == bot.username:
            return
        await bot.chat(f"You said: {message}")

    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
```
