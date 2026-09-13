"""Named Binary Tag (NBT) deserializer."""

from __future__ import annotations

import gzip
import io
import struct
import zlib
from typing import Any, Tuple

from mineflex.errors import PacketError
from mineflex.nbt.tags import (
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


class NBTReader:
    """Deserializer for binary NBT data."""

    def __init__(self, stream: io.BytesIO | bytes) -> None:
        if isinstance(stream, bytes):
            self.stream = io.BytesIO(stream)
        else:
            self.stream = stream

    def _read_exact(self, count: int) -> bytes:
        data = self.stream.read(count)
        if len(data) < count:
            raise PacketError(
                f"Unexpected EOF reading NBT (expected {count} bytes, got {len(data)})"
            )
        return data

    def read_tag_id(self) -> TagType:
        raw = self._read_exact(1)
        tag_int = raw[0]
        try:
            return TagType(tag_int)
        except ValueError:
            raise PacketError(f"Unknown NBT tag type ID: {tag_int}")

    def read_string(self) -> str:
        (length,) = struct.unpack(">H", self._read_exact(2))
        return self._read_exact(length).decode("utf-8", errors="replace")

    def read_payload(self, tag_type: TagType) -> Any:
        if tag_type == TagType.BYTE:
            return TagByte(struct.unpack(">b", self._read_exact(1))[0])
        elif tag_type == TagType.SHORT:
            return TagShort(struct.unpack(">h", self._read_exact(2))[0])
        elif tag_type == TagType.INT:
            return TagInt(struct.unpack(">i", self._read_exact(4))[0])
        elif tag_type == TagType.LONG:
            return TagLong(struct.unpack(">q", self._read_exact(8))[0])
        elif tag_type == TagType.FLOAT:
            return TagFloat(struct.unpack(">f", self._read_exact(4))[0])
        elif tag_type == TagType.DOUBLE:
            return TagDouble(struct.unpack(">d", self._read_exact(8))[0])
        elif tag_type == TagType.BYTE_ARRAY:
            (length,) = struct.unpack(">i", self._read_exact(4))
            return TagByteArray(self._read_exact(length))
        elif tag_type == TagType.STRING:
            return TagString(self.read_string())
        elif tag_type == TagType.LIST:
            item_type = self.read_tag_id()
            (length,) = struct.unpack(">i", self._read_exact(4))
            lst = TagList(item_type=item_type)
            for _ in range(length):
                lst.append(self.read_payload(item_type))
            return lst
        elif tag_type == TagType.COMPOUND:
            compound = TagCompound()
            while True:
                next_type = self.read_tag_id()
                if next_type == TagType.END:
                    break
                name = self.read_string()
                payload = self.read_payload(next_type)
                compound[name] = payload
            return compound
        elif tag_type == TagType.INT_ARRAY:
            (length,) = struct.unpack(">i", self._read_exact(4))
            raw = self._read_exact(length * 4)
            ints = struct.unpack(f">{length}i", raw)
            return TagIntArray(ints)
        elif tag_type == TagType.LONG_ARRAY:
            (length,) = struct.unpack(">i", self._read_exact(4))
            raw = self._read_exact(length * 8)
            longs = struct.unpack(f">{length}q", raw)
            return TagLongArray(longs)
        elif tag_type == TagType.END:
            return None
        else:
            raise PacketError(f"Unhandled NBT tag type: {tag_type}")

    def read_root(self, network_mode: bool = False) -> Tuple[str, TagCompound]:
        """Read root NBT compound. In network mode, the root tag may be unnamed or end tag."""
        tag_type = self.read_tag_id()
        if tag_type == TagType.END:
            return "", TagCompound()
        if tag_type != TagType.COMPOUND:
            raise PacketError(f"Root tag must be Compound or End, got {tag_type}")

        root_name = "" if network_mode else self.read_string()
        compound = self.read_payload(TagType.COMPOUND)
        return root_name, compound


def parse_nbt(data: bytes, network_mode: bool = False) -> TagCompound:
    """Parse binary NBT data, automatically decompressing gzip/zlib if present."""
    if len(data) == 0:
        return TagCompound()
    # Check for gzip header (1f 8b)
    if data[:2] == b"\x1f\x8b":
        data = gzip.decompress(data)
    # Check for zlib header (78 9c or 78 01 or 78 da)
    elif data[:2] in (b"\x78\x9c", b"\x78\x01", b"\x78\xda"):
        try:
            data = zlib.decompress(data)
        except zlib.error:
            pass

    reader = NBTReader(data)
    _, compound = reader.read_root(network_mode=network_mode)
    return compound
