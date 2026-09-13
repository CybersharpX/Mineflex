"""Keep-alive play packets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from mineflex.constants import ProtocolState
from mineflex.protocol.buffer import PacketReader, PacketWriter
from mineflex.protocol.registry import Packet


@dataclass
class KeepAliveClientboundPacket(Packet):
    """Clientbound Keep Alive packet (0x22 in 1.20.1)."""

    packet_id: ClassVar[int] = 0x22
    state: ClassVar[ProtocolState] = ProtocolState.PLAY
    is_serverbound: ClassVar[bool] = False
    name: ClassVar[str] = "keep_alive_clientbound"

    keep_alive_id: int

    def write(self, writer: PacketWriter) -> None:
        writer.write_long(self.keep_alive_id)

    @classmethod
    def decode(cls, reader: PacketReader) -> KeepAliveClientboundPacket:
        return cls(keep_alive_id=reader.read_long())


@dataclass
class KeepAliveServerboundPacket(Packet):
    """Serverbound Keep Alive packet (0x12 in 1.20.1)."""

    packet_id: ClassVar[int] = 0x12
    state: ClassVar[ProtocolState] = ProtocolState.PLAY
    is_serverbound: ClassVar[bool] = True
    name: ClassVar[str] = "keep_alive_serverbound"

    keep_alive_id: int

    def write(self, writer: PacketWriter) -> None:
        writer.write_long(self.keep_alive_id)

    @classmethod
    def decode(cls, reader: PacketReader) -> KeepAliveServerboundPacket:
        return cls(keep_alive_id=reader.read_long())
