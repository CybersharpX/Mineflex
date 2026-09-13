"""Rich Minecraft chat component representations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional

# ANSI color mapping for terminal output
COLOR_TO_ANSI = {
    "black": "\033[30m",
    "dark_blue": "\033[34m",
    "dark_green": "\033[32m",
    "dark_aqua": "\033[36m",
    "dark_red": "\033[31m",
    "dark_purple": "\033[35m",
    "gold": "\033[33m",
    "gray": "\033[37m",
    "dark_gray": "\033[90m",
    "blue": "\033[94m",
    "green": "\033[92m",
    "aqua": "\033[96m",
    "red": "\033[91m",
    "light_purple": "\033[95m",
    "yellow": "\033[93m",
    "white": "\033[97m",
}
ANSI_RESET = "\033[0m"


@dataclass
class ChatComponent:
    """Represents a rich Minecraft chat component tree."""

    text: str = ""
    translate: Optional[str] = None
    with_args: List[ChatComponent] = field(default_factory=list)
    color: Optional[str] = None
    bold: bool = False
    italic: bool = False
    underlined: bool = False
    strikethrough: bool = False
    obfuscated: bool = False
    extra: List[ChatComponent] = field(default_factory=list)
    click_event: Optional[dict[str, Any]] = None
    hover_event: Optional[dict[str, Any]] = None

    def to_plain_text(self) -> str:
        """Flatten this component and its children to plain text without formatting."""
        parts = []
        if self.text:
            parts.append(self.text)
        if self.translate:
            # If with_args exist, format them into translate template
            if self.with_args:
                arg_texts = [arg.to_plain_text() for arg in self.with_args]
                parts.append(f"{self.translate}({', '.join(arg_texts)})")
            else:
                parts.append(self.translate)
        for child in self.extra:
            parts.append(child.to_plain_text())
        return "".join(parts)

    def to_ansi(self) -> str:
        """Render component tree with ANSI terminal color codes."""
        codes = []
        if self.color in COLOR_TO_ANSI:
            codes.append(COLOR_TO_ANSI[self.color])
        if self.bold:
            codes.append("\033[1m")
        if self.italic:
            codes.append("\033[3m")
        if self.underlined:
            codes.append("\033[4m")

        prefix = "".join(codes)
        suffix = ANSI_RESET if prefix else ""

        rendered = prefix + self.to_plain_text() + suffix
        return rendered

    def __str__(self) -> str:
        return self.to_plain_text()

    def __repr__(self) -> str:
        return f"ChatComponent('{self.to_plain_text()}')"
