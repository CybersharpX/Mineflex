"""Packet buffer reading and writing for the Minecraft protocol."""

from __future__ import annotations

import io
import struct
import uuid
from typing import Any, Optional

from mineflex.errors import PacketError
from mineflex.nbt.reader import NBTReader
from mineflex.nbt.tags import TagCompound
from mineflex.nbt.writer import dump_nbt
from mineflex.types import Angle, Position, Vec3


class PacketReader:
    """Reader for parsing Minecraft network protocol primitive types from bytes."""

    __slots__ = ("_data", "_offset", "_length")

    def __init__(self, data: bytes | bytearray | memoryview) -> None:
        self._data = bytes(data)
        self._offset = 0
        self._length = len(self._data)

    @property
    def remaining(self) -> int:
        return self._length - self._offset

    @property
    def offset(self) -> int:
        return self._offset

    def read_bytes(self, count: int) -> bytes:
        if count < 0:
            raise PacketError(f"Negative byte count: {count}")
        if self._offset + count > self._length:
            raise PacketError(
                f"Buffer underflow: requested {count} bytes, but only {self.remaining} available"
            )
        data = self._data[self._offset : self._offset + count]
        self._offset += count
        return data

    def read_remaining(self) -> bytes:
        return self.read_bytes(self.remaining)

    def read_varint(self) -> int:
        """Read a 7-bit variable-length integer (1 to 5 bytes)."""
        value = 0
        position = 0

        while True:
            if self._offset >= self._length:
                raise PacketError("Buffer underflow reading VarInt")
            byte = self._data[self._offset]
            self._offset += 1

            value |= (byte & 0x7F) << position
            if (byte & 0x80) == 0:
                break
            position += 7
            if position >= 35:
                raise PacketError("VarInt is too wide (max 5 bytes)")

        # Convert to signed 32-bit int
        if value & (1 << 31):
            value -= 1 << 32
        return value

    def read_varlong(self) -> int:
        """Read a 7-bit variable-length 64-bit integer (1 to 10 bytes)."""
        value = 0
        position = 0

        while True:
            if self._offset >= self._length:
                raise PacketError("Buffer underflow reading VarLong")
            byte = self._data[self._offset]
            self._offset += 1

            value |= (byte & 0x7F) << position
            if (byte & 0x80) == 0:
                break
            position += 7
            if position >= 70:
                raise PacketError("VarLong is too wide (max 10 bytes)")

        # Convert to signed 64-bit int
        if value & (1 << 63):
            value -= 1 << 64
        return value

    def read_bool(self) -> bool:
        return self.read_ubyte() != 0

    def read_byte(self) -> int:
        return struct.unpack(">b", self.read_bytes(1))[0]

    def read_ubyte(self) -> int:
        return struct.unpack(">B", self.read_bytes(1))[0]

    def read_short(self) -> int:
        return struct.unpack(">h", self.read_bytes(2))[0]

    def read_ushort(self) -> int:
        return struct.unpack(">H", self.read_bytes(2))[0]

    def read_int(self) -> int:
        return struct.unpack(">i", self.read_bytes(4))[0]

    def read_long(self) -> int:
        return struct.unpack(">q", self.read_bytes(8))[0]

    def read_float(self) -> float:
        return struct.unpack(">f", self.read_bytes(4))[0]

    def read_double(self) -> float:
        return struct.unpack(">d", self.read_bytes(8))[0]

    def read_string(self, max_length: int = 32767) -> str:
        length = self.read_varint()
        if length < 0 or length > max_length * 4:
            raise PacketError(f"String length {length} exceeds bounds (max {max_length})")
        data = self.read_bytes(length)
        decoded = data.decode("utf-8", errors="replace")
        if len(decoded) > max_length:
            raise PacketError(f"String character count {len(decoded)} exceeds max {max_length}")
        return decoded

    def read_uuid(self) -> uuid.UUID:
        data = self.read_bytes(16)
        return uuid.UUID(bytes=data)

    def read_position(self) -> Position:
        val = self.read_long()
        return Position.decode(val)

    def read_angle(self) -> Angle:
        byte_val = self.read_ubyte()
        deg = (byte_val * 360.0) / 256.0
        return Angle(deg, 0.0)

    def read_byte_array(self) -> bytes:
        length = self.read_varint()
        return self.read_bytes(length)

    def read_nbt(self) -> Optional[TagCompound]:
        if self.remaining == 0:
            return None
        # Peek first byte to see if End tag (0x00)
        first_byte = self._data[self._offset]
        if first_byte == 0:
            self._offset += 1
            return None
        # Use NBTReader in network mode
        stream = io.BytesIO(self._data[self._offset :])
        reader = NBTReader(stream)
        _, compound = reader.read_root(network_mode=True)
        consumed = stream.tell()
        self._offset += consumed
        return compound

    def read_slot(self) -> Optional[dict[str, Any]]:
        """Read a Minecraft slot/ItemStack."""
        present = self.read_bool()
        if not present:
            return None
        item_id = self.read_varint()
        item_count = self.read_byte()
        nbt = self.read_nbt()
        return {
            "id": item_id,
            "count": item_count,
            "nbt": nbt,
        }


class PacketWriter:
    """Writer for encoding Minecraft network protocol primitive types into bytes."""

    __slots__ = ("_buffer",)

    def __init__(self) -> None:
        self._buffer = bytearray()

    def get_bytes(self) -> bytes:
        return bytes(self._buffer)

    def write_bytes(self, data: bytes | bytearray) -> None:
        self._buffer.extend(data)

    def write_varint(self, value: int) -> None:
        """Encode integer as 7-bit variable-length bytes."""
        value &= 0xFFFFFFFF  # Mask to unsigned 32-bit
        while True:
            byte = value & 0x7F
            value >>= 7
            if value:
                self._buffer.append(byte | 0x80)
            else:
                self._buffer.append(byte)
                break

    def write_varlong(self, value: int) -> None:
        """Encode 64-bit integer as 7-bit variable-length bytes."""
        value &= 0xFFFFFFFFFFFFFFFF
        while True:
            byte = value & 0x7F
            value >>= 7
            if value:
                self._buffer.append(byte | 0x80)
            else:
                self._buffer.append(byte)
                break

    def write_bool(self, value: bool) -> None:
        self.write_ubyte(1 if value else 0)

    def write_byte(self, value: int) -> None:
        self._buffer.extend(struct.pack(">b", value))

    def write_ubyte(self, value: int) -> None:
        self._buffer.extend(struct.pack(">B", value))

    def write_short(self, value: int) -> None:
        self._buffer.extend(struct.pack(">h", value))

    def write_ushort(self, value: int) -> None:
        self._buffer.extend(struct.pack(">H", value))

    def write_int(self, value: int) -> None:
        self._buffer.extend(struct.pack(">i", value))

    def write_long(self, value: int) -> None:
        self._buffer.extend(struct.pack(">q", value))

    def write_float(self, value: float) -> None:
        self._buffer.extend(struct.pack(">f", value))

    def write_double(self, value: float) -> None:
        self._buffer.extend(struct.pack(">d", value))

    def write_string(self, value: str) -> None:
        encoded = value.encode("utf-8")
        self.write_varint(len(encoded))
        self.write_bytes(encoded)

    def write_uuid(self, value: uuid.UUID | str) -> None:
        if isinstance(value, str):
            value = uuid.UUID(value)
        self.write_bytes(value.bytes)

    def write_position(self, value: Position | Vec3) -> None:
        pos = Position.from_vec3(value) if isinstance(value, Vec3) else value
        self.write_long(pos.encode())

    def write_angle(self, value: Angle) -> None:
        byte_val = int((value.yaw % 360) * 256 / 360) & 0xFF
        self.write_ubyte(byte_val)

    def write_byte_array(self, data: bytes) -> None:
        self.write_varint(len(data))
        self.write_bytes(data)

    def write_nbt(self, value: Optional[TagCompound | dict[str, Any]]) -> None:
        if value is None:
            self.write_ubyte(0)  # TAG_End
            return
        nbt_data = dump_nbt(value, network_mode=True)
        self.write_bytes(nbt_data)

    def write_slot(self, slot: Optional[dict[str, Any]]) -> None:
        if slot is None or slot.get("count", 0) <= 0:
            self.write_bool(False)
            return
        self.write_bool(True)
        self.write_varint(slot["id"])
        self.write_byte(slot["count"])
        self.write_nbt(slot.get("nbt"))
