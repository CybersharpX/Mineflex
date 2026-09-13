"""Chat message parsers for JSON and legacy formats."""

from __future__ import annotations

import json
from typing import Any, Union

from mineflex.chat.component import ChatComponent

LEGACY_COLOR_CODES = {
    "0": "black",
    "1": "dark_blue",
    "2": "dark_green",
    "3": "dark_aqua",
    "4": "dark_red",
    "5": "dark_purple",
    "6": "gold",
    "7": "gray",
    "8": "dark_gray",
    "9": "blue",
    "a": "green",
    "b": "aqua",
    "c": "red",
    "d": "light_purple",
    "e": "yellow",
    "f": "white",
}


def parse_chat(raw_data: Union[str, dict[str, Any], list[Any]]) -> ChatComponent:
    """Parse raw chat data (JSON string, dict, list, or legacy formatted string)."""
    if isinstance(raw_data, str):
        # Try JSON first
        trimmed = raw_data.strip()
        if (trimmed.startswith("{") and trimmed.endswith("}")) or (
            trimmed.startswith("[") and trimmed.endswith("]")
        ):
            try:
                parsed_json = json.loads(trimmed)
                return parse_chat(parsed_json)
            except Exception:
                pass
        # Check for legacy § formatting
        if "§" in raw_data:
            return parse_legacy_chat(raw_data)
        return ChatComponent(text=raw_data)

    if isinstance(raw_data, list):
        root = ChatComponent()
        root.extra = [parse_chat(item) for item in raw_data]
        return root

    if isinstance(raw_data, dict):
        text = str(raw_data.get("text", ""))
        translate = raw_data.get("translate")
        color = raw_data.get("color")
        bold = bool(raw_data.get("bold", False))
        italic = bool(raw_data.get("italic", False))
        underlined = bool(raw_data.get("underlined", False))
        strikethrough = bool(raw_data.get("strikethrough", False))
        obfuscated = bool(raw_data.get("obfuscated", False))

        with_args = []
        if "with" in raw_data and isinstance(raw_data["with"], list):
            with_args = [parse_chat(arg) for arg in raw_data["with"]]

        extra = []
        if "extra" in raw_data and isinstance(raw_data["extra"], list):
            extra = [parse_chat(child) for child in raw_data["extra"]]

        return ChatComponent(
            text=text,
            translate=translate,
            with_args=with_args,
            color=color,
            bold=bold,
            italic=italic,
            underlined=underlined,
            strikethrough=strikethrough,
            obfuscated=obfuscated,
            extra=extra,
            click_event=raw_data.get("clickEvent"),
            hover_event=raw_data.get("hoverEvent"),
        )

    return ChatComponent(text=str(raw_data))


def parse_legacy_chat(text: str) -> ChatComponent:
    """Parse legacy Minecraft formatting codes (e.g. §cRed text §aGreen text)."""
    parts = text.split("§")
    root = ChatComponent(text=parts[0])

    current_color = None
    bold = False
    italic = False
    underlined = False

    for part in parts[1:]:
        if not part:
            continue
        code = part[0].lower()
        chunk_text = part[1:]

        if code in LEGACY_COLOR_CODES:
            current_color = LEGACY_COLOR_CODES[code]
            bold = False
            italic = False
            underlined = False
        elif code == "l":
            bold = True
        elif code == "o":
            italic = True
        elif code == "n":
            underlined = True
        elif code == "r":
            current_color = None
            bold = False
            italic = False
            underlined = False

        if chunk_text:
            child = ChatComponent(
                text=chunk_text,
                color=current_color,
                bold=bold,
                italic=italic,
                underlined=underlined,
            )
            root.extra.append(child)

    return root
