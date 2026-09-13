"""World and chunk play packets."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar, Optional

from mineflex.constants import ProtocolState
from mineflex.nbt.tags import TagCompound
from mineflex.protocol.buffer import PacketReader, PacketWriter
from mineflex.protocol.registry import Packet
from mineflex.types import Position


@dataclass
class BlockUpdatePacket(Packet):
    """Clientbound Block Update packet (0x09 in 1.20.1)."""

    packet_id: ClassVar[int] = 0x09
    state: ClassVar[ProtocolState] = ProtocolState.PLAY
    is_serverbound: ClassVar[bool] = False
    name: ClassVar[str] = "block_update"

    pos: Position
    block_state_id: int

    def write(self, writer: PacketWriter) -> None:
        writer.write_position(self.pos)
        writer.write_varint(self.block_state_id)

    @classmethod
    def decode(cls, reader: PacketReader) -> BlockUpdatePacket:
        return cls(
            pos=reader.read_position(),
            block_state_id=reader.read_varint(),
        )


@dataclass
class ChunkDataPacket(Packet):
    """Clientbound Chunk Data and Update Light packet (0x24 in 1.20.1)."""

    packet_id: ClassVar[int] = 0x24
    state: ClassVar[ProtocolState] = ProtocolState.PLAY
    is_serverbound: ClassVar[bool] = False
    name: ClassVar[str] = "chunk_data"

    chunk_x: int
    chunk_z: int
    heightmaps: Optional[TagCompound]
    data: bytes
    block_entities: list = field(default_factory=list)

    def write(self, writer: PacketWriter) -> None:
        writer.write_int(self.chunk_x)
        writer.write_int(self.chunk_z)
        writer.write_nbt(self.heightmaps or TagCompound())
        writer.write_byte_array(self.data)
        writer.write_varint(len(self.block_entities))
        # Light data skipped / zeroed for simplicity
        writer.write_bool(True)  # Trust edges
        writer.write_varint(0)  # Sky light mask
        writer.write_varint(0)  # Block light mask
        writer.write_varint(0)  # Empty sky light mask
        writer.write_varint(0)  # Empty block light mask
        writer.write_varint(0)  # Sky light array count
        writer.write_varint(0)  # Block light array count

    @classmethod
    def decode(cls, reader: PacketReader) -> ChunkDataPacket:
        chunk_x = reader.read_int()
        chunk_z = reader.read_int()
        heightmaps = reader.read_nbt()
        data = reader.read_byte_array()
        num_block_entities = reader.read_varint()
        # Read block entities if present
        block_entities = []
        for _ in range(num_block_entities):
            packed_xz = reader.read_ubyte()
            y = reader.read_short()
            be_type = reader.read_varint()
            be_nbt = reader.read_nbt()
            block_entities.append({"packed_xz": packed_xz, "y": y, "type": be_type, "nbt": be_nbt})
        # Ignore remaining light data if present
        if reader.remaining > 0:
            reader.read_remaining()
        return cls(
            chunk_x=chunk_x,
            chunk_z=chunk_z,
            heightmaps=heightmaps,
            data=data,
            block_entities=block_entities,
        )
