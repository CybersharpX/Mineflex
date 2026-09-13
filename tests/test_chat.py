"""Unit tests for chat components and parsers."""

import json

from mineflex.chat import parse_chat


def test_plain_text_and_json_parsing():
    raw_json = json.dumps(
        {
            "text": "Hello ",
            "color": "yellow",
            "bold": True,
            "extra": [{"text": "World!", "color": "green", "bold": False}],
        }
    )

    comp = parse_chat(raw_json)
    assert comp.to_plain_text() == "Hello World!"
    assert comp.color == "yellow"
    assert comp.bold is True
    assert len(comp.extra) == 1
    assert comp.extra[0].color == "green"
    assert comp.extra[0].bold is False


def test_translate_component():
    raw = {"translate": "chat.type.text", "with": [{"text": "Player1"}, {"text": "Good morning!"}]}
    comp = parse_chat(raw)
    assert "Player1" in comp.to_plain_text()
    assert "Good morning!" in comp.to_plain_text()


def test_legacy_section_formatting():
    legacy_str = "§eWelcome to §bMineflex§r!"
    comp = parse_chat(legacy_str)
    assert comp.to_plain_text() == "Welcome to Mineflex!"
    assert len(comp.extra) == 3
    assert comp.extra[0].color == "yellow"
    assert comp.extra[0].text == "Welcome to "
    assert comp.extra[1].color == "aqua"
    assert comp.extra[1].text == "Mineflex"
    assert comp.extra[2].color is None
    assert comp.extra[2].text == "!"
