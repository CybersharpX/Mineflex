"""Handshake state packets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from mineflex.constants import ProtocolState
from mineflex.protocol.buffer import PacketReader, PacketWriter
from mineflex.protocol.registry import Packet


@dataclass
class HandshakePacket(Packet):
    """Serverbound Handshake packet (0x00)."""

    packet_id: ClassVar[int] = 0x00
    state: ClassVar[ProtocolState] = ProtocolState.HANDSHAKING
    is_serverbound: ClassVar[bool] = True
    name: ClassVar[str] = "handshake"

    protocol_version: int
    server_address: str
    server_port: int
    next_state: int  # 1 for status, 2 for login

    def write(self, writer: PacketWriter) -> None:
        writer.write_varint(self.protocol_version)
        writer.write_string(self.server_address)
        writer.write_ushort(self.server_port)
        writer.write_varint(self.next_state)

    @classmethod
    def decode(cls, reader: PacketReader) -> HandshakePacket:
        return cls(
            protocol_version=reader.read_varint(),
            server_address=reader.read_string(),
            server_port=reader.read_ushort(),
            next_state=reader.read_varint(),
        )
