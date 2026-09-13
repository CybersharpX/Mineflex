"""Internal plugin for handling chat events, patterns, and message dispatch."""

from __future__ import annotations

import asyncio
import re
from typing import TYPE_CHECKING, Optional, Pattern, Union

from mineflex.chat.component import ChatComponent
from mineflex.chat.parser import parse_chat
from mineflex.protocol.packets.play.chat import ChatMessagePacket, SystemChatPacket

if TYPE_CHECKING:
    from mineflex.bot import Bot

# Standard Minecraft chat format "<Player> Hello"
CHAT_PATTERN = re.compile(r"^<([a-zA-Z0-9_]{1,16})>\s*(.*)$")
WHISPER_PATTERN = re.compile(r"^([a-zA-Z0-9_]{1,16})\s+whispers:\s*(.*)$")


def inject_chat(bot: Bot) -> None:
    if getattr(bot, "_chat_injected", False):
        return
    bot._chat_injected = True  # type: ignore
    bot.chat_patterns = []

    async def chat(message: str) -> None:
        """Send a public chat message to the server."""
        if not bot.client or not bot.client.is_connected:
            return
        packet = ChatMessagePacket(message=message)
        await bot.client.send_packet(packet)

    async def whisper(username: str, message: str) -> None:
        """Send a private whisper message to a player."""
        await chat(f"/tell {username} {message}")

    def add_chat_pattern(
        name: str,
        pattern: Union[Pattern[str], str],
        chat_type: str = "chat",
    ) -> None:
        """Register a named regex pattern to match against incoming chat messages."""
        compiled = re.compile(pattern) if isinstance(pattern, str) else pattern
        bot.chat_patterns.append((name, compiled, chat_type))

    def remove_chat_pattern(name: str) -> None:
        """Remove a registered chat pattern by name."""
        bot.chat_patterns = [(n, p, t) for (n, p, t) in bot.chat_patterns if n != name]

    async def await_message(
        pattern: Union[Pattern[str], str],
        timeout: Optional[float] = None,
    ) -> str:
        """Wait asynchronously until a chat message matching pattern is received."""
        compiled = re.compile(pattern) if isinstance(pattern, str) else pattern
        fut: asyncio.Future[str] = asyncio.get_running_loop().create_future()

        def on_message(comp: ChatComponent, overlay: bool = False) -> None:
            text = comp.to_plain_text()
            if compiled.search(text) and not fut.done():
                fut.set_result(text)

        bot.on("message", on_message)
        try:
            if timeout is not None:
                return await asyncio.wait_for(fut, timeout=timeout)
            return await fut
        finally:
            bot.off("message", on_message)

    bot.chat = chat  # type: ignore
    bot.whisper = whisper  # type: ignore
    bot.add_chat_pattern = add_chat_pattern  # type: ignore
    bot.remove_chat_pattern = remove_chat_pattern  # type: ignore
    bot.await_message = await_message  # type: ignore

    def on_system_chat(packet: SystemChatPacket) -> None:
        comp = parse_chat(packet.content)
        plain_text = comp.to_plain_text()

        bot.emit_sync("message", comp, packet.overlay)
        bot.emit_sync("messagestr", plain_text, packet.overlay, comp)

        if packet.overlay:
            bot.emit_sync("action_bar", comp)

        # Standard public chat pattern
        match = CHAT_PATTERN.match(plain_text)
        if match:
            username = match.group(1)
            msg = match.group(2)
            bot.emit_sync("chat", username, msg, comp, [msg])

        # Standard whisper pattern
        whisper_match = WHISPER_PATTERN.match(plain_text)
        if whisper_match:
            username = whisper_match.group(1)
            msg = whisper_match.group(2)
            bot.emit_sync("whisper", username, msg, comp, [msg])

        # User-registered chat patterns
        for name, pat, ctype in bot.chat_patterns:
            m = pat.search(plain_text)
            if m:
                groups = list(m.groups())
                bot.emit_sync(f"chat:{name}", groups, plain_text, comp)

    bot.client.register_handler(SystemChatPacket, on_system_chat)
