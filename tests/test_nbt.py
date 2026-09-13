"""Unit tests for NBT tags, reader, and writer."""

from mineflex.nbt import (
    TagByte,
    TagByteArray,
    TagCompound,
    TagFloat,
    TagInt,
    TagIntArray,
    TagList,
    TagLongArray,
    TagString,
    TagType,
    dump_nbt,
    parse_nbt,
)


def test_nbt_compound_roundtrip():
    compound = TagCompound(
        {
            "name": TagString("MineflexBot"),
            "health": TagFloat(20.0),
            "score": TagInt(100),
            "is_active": TagByte(1),
            "inventory": TagList(TagType.STRING, [TagString("sword"), TagString("shield")]),
            "sub": TagCompound({"key": TagString("value")}),
        }
    )

    serialized = dump_nbt(compound, name="RootTag")
    parsed = parse_nbt(serialized)

    assert parsed["name"].val == "MineflexBot"
    assert parsed["health"].val == 20.0
    assert parsed["score"].val == 100
    assert parsed["is_active"].val == 1
    assert len(parsed["inventory"]) == 2
    assert parsed["inventory"][0].val == "sword"
    assert parsed["inventory"][1].val == "shield"
    assert parsed["sub"]["key"].val == "value"


def test_nbt_network_mode():
    compound = TagCompound(
        {
            "Damage": TagInt(5),
            "Unbreakable": TagByte(1),
        }
    )

    serialized = dump_nbt(compound, network_mode=True)
    parsed = parse_nbt(serialized, network_mode=True)

    assert parsed["Damage"].val == 5
    assert parsed["Unbreakable"].val == 1


def test_nbt_arrays():
    compound = TagCompound(
        {
            "bytes": TagByteArray(b"\x01\x02\x03\x04"),
            "ints": TagIntArray((10, 20, 30)),
            "longs": TagLongArray((10000000000, 20000000000)),
        }
    )

    serialized = dump_nbt(compound)
    parsed = parse_nbt(serialized)

    assert parsed["bytes"].val == b"\x01\x02\x03\x04"
    assert parsed["ints"].val == (10, 20, 30)
    assert parsed["longs"].val == (10000000000, 20000000000)
