"""Bot checking recipes and crafting items."""

import asyncio

from mineflex import create_bot


async def main() -> None:
    bot = create_bot(
        host="localhost",
        port=25565,
        username="Crafter",
        auth="offline",
    )

    @bot.on("chat")
    async def on_chat(username: str, message: str, *args):
        if message.startswith("!recipe "):
            item_name = message.split(" ", 1)[1].strip()
            matching_recipes = [r for r in bot.registry.recipes if r.name == item_name]

            if not matching_recipes:
                await bot.chat(f"No recipe found for '{item_name}'.")
                return

            recipe = matching_recipes[0]
            ing_names = []
            for ing_id in recipe.ingredients:
                ing_def = bot.registry.items.get(ing_id)
                ing_names.append(ing_def.name if ing_def else str(ing_id))

            ingredients_str = ", ".join(ing_names)
            await bot.chat(
                f"Recipe for {item_name} yields {recipe.result_count} items from: {ingredients_str}"
            )

    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
