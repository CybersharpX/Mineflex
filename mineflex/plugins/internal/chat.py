"""Internal plugin for handling chat events and sending chat messages."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from mineflex.chat.parser import parse_chat
from mineflex.protocol.packets.play.chat import ChatMessagePacket, SystemChatPacket

if TYPE_CHECKING:
    from mineflex.bot import Bot

# Regex pattern to extract username and message from standard Minecraft chat format "<Player> Hello"
CHAT_PATTERN = re.compile(r"^<([a-zA-Z0-9_]{1,16})>\s*(.*)$")


def inject_chat(bot: Bot) -> None:
    """Inject chat handling capabilities into the bot."""

    async def chat(message: str) -> None:
        """Send a public chat message to the server."""
        if not bot.client or not bot.client.is_connected:
            return
        packet = ChatMessagePacket(message=message)
        await bot.client.send_packet(packet)

    async def whisper(username: str, message: str) -> None:
        """Send a private whisper message to a player."""
        await chat(f"/tell {username} {message}")

    bot.chat = chat  # type: ignore
    bot.whisper = whisper  # type: ignore

    def on_system_chat(packet: SystemChatPacket) -> None:
        comp = parse_chat(packet.content)
        plain_text = comp.to_plain_text()

        bot.emit_sync("message", comp, packet.overlay)

        # Check if chat format <Username> Message
        match = CHAT_PATTERN.match(plain_text)
        if match:
            username = match.group(1)
            msg = match.group(2)
            bot.emit_sync("chat", username, msg, plain_text)

    bot.client.register_handler(SystemChatPacket, on_system_chat)
