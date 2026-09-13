"""Bot that inspects and manages inventory items."""

import asyncio

from mineflex import create_bot


async def main() -> None:
    bot = create_bot(
        host="localhost",
        port=25565,
        username="Quartermaster",
        auth="offline",
    )

    @bot.on("chat")
    async def on_chat(username: str, message: str, *args):
        if message == "!inv":
            items = []
            for slot_idx in range(9, 45):
                item = bot.inventory.get_slot(slot_idx)
                if item:
                    items.append(f"{item.name} x{item.count}")

            if items:
                await bot.chat("Inventory: " + ", ".join(items[:8]))
            else:
                await bot.chat("Inventory is currently empty.")

        elif message.startswith("!equip "):
            item_name = message.split(" ", 1)[1].strip()
            try:
                await bot.equip(item_name)
                await bot.chat(f"Equipped {item_name} to main hand.")
            except Exception as exc:
                await bot.chat(f"Cannot equip {item_name}: {exc}")

        elif message.startswith("!drop "):
            item_name = message.split(" ", 1)[1].strip()
            item = bot.inventory.find_inventory_item(item_name)
            if item:
                await bot.equip(item)
                await bot.toss(item.id, count=item.count)
                await bot.chat(f"Dropped {item.name}.")
            else:
                await bot.chat(f"No {item_name} found in inventory.")

    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
