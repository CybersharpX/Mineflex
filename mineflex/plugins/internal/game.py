"""Internal plugins for health, game status, and time tracking."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mineflex.protocol.packets.play.player import (
    LoginPlayPacket,
    SetExperiencePacket,
    SetHealthPacket,
    UpdateTimePacket,
)

if TYPE_CHECKING:
    from mineflex.bot import Bot


def inject_health(bot: Bot) -> None:
    """Inject health and experience tracking into bot."""
    bot.health = 20.0
    bot.food = 20
    bot.food_saturation = 5.0
    bot.experience = {"level": 0, "points": 0, "progress": 0.0}

    def on_set_health(packet: SetHealthPacket) -> None:
        old_health = bot.health
        bot.health = packet.health
        bot.food = packet.food
        bot.food_saturation = packet.food_saturation
        bot.emit_sync("health", bot.health, bot.food)
        if old_health > 0 and bot.health <= 0:
            bot.emit_sync("death")

    def on_set_experience(packet: SetExperiencePacket) -> None:
        bot.experience = {
            "level": packet.level,
            "points": packet.total_experience,
            "progress": packet.experience_bar,
        }
        bot.emit_sync("experience", bot.experience)

    bot.client.register_handler(SetHealthPacket, on_set_health)
    bot.client.register_handler(SetExperiencePacket, on_set_experience)


def inject_game(bot: Bot) -> None:
    """Inject game mode and dimension tracking into bot."""
    bot.game_mode = "survival"
    bot.dimension = "minecraft:overworld"
    bot.is_hardcore = False

    def on_login_play(packet: LoginPlayPacket) -> None:
        gm_map = {0: "survival", 1: "creative", 2: "adventure", 3: "spectator"}
        bot.game_mode = gm_map.get(packet.gamemode, "survival")
        bot.dimension = packet.dimension_name
        bot.is_hardcore = packet.is_hardcore
        bot.emit_sync("game", bot.game_mode, bot.dimension)

    bot.client.register_handler(LoginPlayPacket, on_login_play)


def inject_time(bot: Bot) -> None:
    """Inject world time tracking into bot."""
    bot.time = 0
    bot.day = 0
    bot.time_of_day = 0
    bot.is_raining = False

    def on_update_time(packet: UpdateTimePacket) -> None:
        bot.time = packet.world_age
        bot.time_of_day = abs(packet.time_of_day) % 24000
        bot.day = abs(packet.world_age) // 24000
        bot.emit_sync("time", bot.time_of_day, bot.time)

    bot.client.register_handler(UpdateTimePacket, on_update_time)
