"""Named Binary Tag (NBT) serializer."""

from __future__ import annotations

import io
import struct
from typing import Any

from mineflex.errors import PacketError
from mineflex.nbt.tags import (
    NBTTag,
    TagByte,
    TagByteArray,
    TagCompound,
    TagDouble,
    TagFloat,
    TagInt,
    TagIntArray,
    TagList,
    TagLong,
    TagLongArray,
    TagShort,
    TagString,
    TagType,
)


class NBTWriter:
    """Serializer for binary NBT data."""

    def __init__(self, stream: io.BytesIO | None = None) -> None:
        self.stream = stream or io.BytesIO()

    def write_tag_id(self, tag_type: TagType) -> None:
        self.stream.write(bytes([int(tag_type)]))

    def write_string(self, text: str) -> None:
        encoded = text.encode("utf-8")
        self.stream.write(struct.pack(">H", len(encoded)))
        self.stream.write(encoded)

    def write_payload(self, tag: Any) -> None:
        if isinstance(tag, TagByte) or (isinstance(tag, int) and -128 <= tag <= 127):
            val = tag.val if isinstance(tag, TagByte) else tag
            self.stream.write(struct.pack(">b", val))
        elif isinstance(tag, TagShort):
            self.stream.write(struct.pack(">h", tag.val))
        elif isinstance(tag, TagInt) or isinstance(tag, int):
            val = tag.val if isinstance(tag, TagInt) else tag
            self.stream.write(struct.pack(">i", val))
        elif isinstance(tag, TagLong):
            self.stream.write(struct.pack(">q", tag.val))
        elif isinstance(tag, TagFloat):
            self.stream.write(struct.pack(">f", tag.val))
        elif isinstance(tag, TagDouble) or isinstance(tag, float):
            val = tag.val if isinstance(tag, TagDouble) else tag
            self.stream.write(struct.pack(">d", val))
        elif isinstance(tag, TagByteArray) or isinstance(tag, (bytes, bytearray)):
            val = tag.val if isinstance(tag, TagByteArray) else bytes(tag)
            self.stream.write(struct.pack(">i", len(val)))
            self.stream.write(val)
        elif isinstance(tag, TagString) or isinstance(tag, str):
            val = tag.val if isinstance(tag, TagString) else tag
            self.write_string(val)
        elif isinstance(tag, TagList):
            self.write_tag_id(tag.item_type)
            self.stream.write(struct.pack(">i", len(tag)))
            for item in tag:
                self.write_payload(item)
        elif isinstance(tag, TagCompound) or isinstance(tag, dict):
            items = tag.items() if isinstance(tag, dict) else tag._tags.items()
            for key, val in items:
                inferred_type = self._infer_tag_type(val)
                self.write_tag_id(inferred_type)
                self.write_string(key)
                self.write_payload(val)
            self.write_tag_id(TagType.END)
        elif isinstance(tag, TagIntArray):
            self.stream.write(struct.pack(">i", len(tag.val)))
            for v in tag.val:
                self.stream.write(struct.pack(">i", v))
        elif isinstance(tag, TagLongArray):
            self.stream.write(struct.pack(">i", len(tag.val)))
            for v in tag.val:
                self.stream.write(struct.pack(">q", v))
        else:
            raise PacketError(f"Unsupported NBT tag for serialization: {type(tag)}")

    def _infer_tag_type(self, val: Any) -> TagType:
        if isinstance(val, NBTTag):
            return val.tag_type
        if isinstance(val, bool):
            return TagType.BYTE
        if isinstance(val, int):
            return TagType.INT
        if isinstance(val, float):
            return TagType.DOUBLE
        if isinstance(val, str):
            return TagType.STRING
        if isinstance(val, (bytes, bytearray)):
            return TagType.BYTE_ARRAY
        if isinstance(val, list):
            return TagType.LIST
        if isinstance(val, dict):
            return TagType.COMPOUND
        raise PacketError(f"Cannot infer NBT tag type for: {type(val)}")

    def write_root(
        self, compound: TagCompound | dict[str, Any], name: str = "", network_mode: bool = False
    ) -> bytes:
        """Serialize root compound tag."""
        self.write_tag_id(TagType.COMPOUND)
        if not network_mode:
            self.write_string(name)
        self.write_payload(compound)
        return self.stream.getvalue()


def dump_nbt(
    compound: TagCompound | dict[str, Any], name: str = "", network_mode: bool = False
) -> bytes:
    """Serialize NBT compound to bytes."""
    writer = NBTWriter()
    return writer.write_root(compound, name=name, network_mode=network_mode)
