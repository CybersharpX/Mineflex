"""Chat and system message play packets."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import ClassVar

from mineflex.constants import ProtocolState
from mineflex.protocol.buffer import PacketReader, PacketWriter
from mineflex.protocol.registry import Packet


@dataclass
class SystemChatPacket(Packet):
    """Clientbound System Chat Message packet (0x62 in 1.20.1)."""

    packet_id: ClassVar[int] = 0x62
    state: ClassVar[ProtocolState] = ProtocolState.PLAY
    is_serverbound: ClassVar[bool] = False
    name: ClassVar[str] = "system_chat"

    content: str
    overlay: bool

    def write(self, writer: PacketWriter) -> None:
        writer.write_string(self.content)
        writer.write_bool(self.overlay)

    @classmethod
    def decode(cls, reader: PacketReader) -> SystemChatPacket:
        return cls(content=reader.read_string(), overlay=reader.read_bool())


@dataclass
class DisconnectPlayPacket(Packet):
    """Clientbound Disconnect packet during Play (0x1E in 1.20.1)."""

    packet_id: ClassVar[int] = 0x1E
    state: ClassVar[ProtocolState] = ProtocolState.PLAY
    is_serverbound: ClassVar[bool] = False
    name: ClassVar[str] = "play_disconnect"

    reason: str

    def write(self, writer: PacketWriter) -> None:
        writer.write_string(self.reason)

    @classmethod
    def decode(cls, reader: PacketReader) -> DisconnectPlayPacket:
        return cls(reason=reader.read_string())


@dataclass
class ChatMessagePacket(Packet):
    """Serverbound Chat Message packet (0x04 in 1.20.1)."""

    packet_id: ClassVar[int] = 0x04
    state: ClassVar[ProtocolState] = ProtocolState.PLAY
    is_serverbound: ClassVar[bool] = True
    name: ClassVar[str] = "chat_message"

    message: str
    timestamp: int = 0
    salt: int = 0

    def write(self, writer: PacketWriter) -> None:
        ts = self.timestamp if self.timestamp != 0 else int(time.time() * 1000)
        writer.write_string(self.message)
        writer.write_long(ts)
        writer.write_long(self.salt)
        writer.write_bool(False)  # Has signature
        writer.write_varint(0)  # Message count
        # Bitset of acknowledged messages (20 bits in 1.20.1, written as 3 bytes / bitset)
        writer.write_varint(0)

    @classmethod
    def decode(cls, reader: PacketReader) -> ChatMessagePacket:
        message = reader.read_string()
        ts = reader.read_long()
        salt = reader.read_long()
        if reader.remaining > 0:
            reader.read_remaining()
        return cls(message=message, timestamp=ts, salt=salt)
