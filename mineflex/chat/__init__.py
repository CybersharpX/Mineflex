"""Minecraft chat representations and parsers."""

from __future__ import annotations

from mineflex.chat.component import ChatComponent
from mineflex.chat.parser import parse_chat, parse_legacy_chat

__all__ = ["ChatComponent", "parse_chat", "parse_legacy_chat"]
