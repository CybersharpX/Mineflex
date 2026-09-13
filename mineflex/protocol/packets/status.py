"""Status state packets (Server List Ping)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from mineflex.constants import ProtocolState
from mineflex.protocol.buffer import PacketReader, PacketWriter
from mineflex.protocol.registry import Packet


@dataclass
class StatusRequestPacket(Packet):
    """Serverbound Status Request packet (0x00)."""

    packet_id: ClassVar[int] = 0x00
    state: ClassVar[ProtocolState] = ProtocolState.STATUS
    is_serverbound: ClassVar[bool] = True
    name: ClassVar[str] = "status_request"

    @classmethod
    def decode(cls, reader: PacketReader) -> StatusRequestPacket:
        return cls()


@dataclass
class StatusResponsePacket(Packet):
    """Clientbound Status Response packet (0x00)."""

    packet_id: ClassVar[int] = 0x00
    state: ClassVar[ProtocolState] = ProtocolState.STATUS
    is_serverbound: ClassVar[bool] = False
    name: ClassVar[str] = "status_response"

    response_json: str

    def write(self, writer: PacketWriter) -> None:
        writer.write_string(self.response_json)

    @classmethod
    def decode(cls, reader: PacketReader) -> StatusResponsePacket:
        return cls(response_json=reader.read_string())


@dataclass
class PingPacket(Packet):
    """Serverbound Ping packet (0x01)."""

    packet_id: ClassVar[int] = 0x01
    state: ClassVar[ProtocolState] = ProtocolState.STATUS
    is_serverbound: ClassVar[bool] = True
    name: ClassVar[str] = "ping"

    time: int

    def write(self, writer: PacketWriter) -> None:
        writer.write_long(self.time)

    @classmethod
    def decode(cls, reader: PacketReader) -> PingPacket:
        return cls(time=reader.read_long())


@dataclass
class PongPacket(Packet):
    """Clientbound Pong packet (0x01)."""

    packet_id: ClassVar[int] = 0x01
    state: ClassVar[ProtocolState] = ProtocolState.STATUS
    is_serverbound: ClassVar[bool] = False
    name: ClassVar[str] = "pong"

    time: int

    def write(self, writer: PacketWriter) -> None:
        writer.write_long(self.time)

    @classmethod
    def decode(cls, reader: PacketReader) -> PongPacket:
        return cls(time=reader.read_long())
