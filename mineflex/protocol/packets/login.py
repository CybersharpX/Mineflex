"""Login state packets."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import ClassVar, Optional

from mineflex.constants import ProtocolState
from mineflex.protocol.buffer import PacketReader, PacketWriter
from mineflex.protocol.registry import Packet


@dataclass
class LoginStartPacket(Packet):
    """Serverbound Login Start packet (0x00)."""

    packet_id: ClassVar[int] = 0x00
    state: ClassVar[ProtocolState] = ProtocolState.LOGIN
    is_serverbound: ClassVar[bool] = True
    name: ClassVar[str] = "login_start"

    name_str: str
    player_uuid: Optional[uuid.UUID] = None

    def write(self, writer: PacketWriter) -> None:
        writer.write_string(self.name_str)
        if self.player_uuid is not None:
            writer.write_bool(True)
            writer.write_uuid(self.player_uuid)
        else:
            writer.write_bool(False)

    @classmethod
    def decode(cls, reader: PacketReader) -> LoginStartPacket:
        name_str = reader.read_string()
        has_uuid = reader.read_bool() if reader.remaining > 0 else False
        player_uuid = reader.read_uuid() if has_uuid else None
        return cls(name_str=name_str, player_uuid=player_uuid)


@dataclass
class DisconnectLoginPacket(Packet):
    """Clientbound Disconnect packet during Login (0x00)."""

    packet_id: ClassVar[int] = 0x00
    state: ClassVar[ProtocolState] = ProtocolState.LOGIN
    is_serverbound: ClassVar[bool] = False
    name: ClassVar[str] = "login_disconnect"

    reason: str

    def write(self, writer: PacketWriter) -> None:
        writer.write_string(self.reason)

    @classmethod
    def decode(cls, reader: PacketReader) -> DisconnectLoginPacket:
        return cls(reason=reader.read_string())


@dataclass
class EncryptionRequestPacket(Packet):
    """Clientbound Encryption Request packet (0x01)."""

    packet_id: ClassVar[int] = 0x01
    state: ClassVar[ProtocolState] = ProtocolState.LOGIN
    is_serverbound: ClassVar[bool] = False
    name: ClassVar[str] = "encryption_request"

    server_id: str
    public_key: bytes
    verify_token: bytes

    def write(self, writer: PacketWriter) -> None:
        writer.write_string(self.server_id)
        writer.write_byte_array(self.public_key)
        writer.write_byte_array(self.verify_token)

    @classmethod
    def decode(cls, reader: PacketReader) -> EncryptionRequestPacket:
        return cls(
            server_id=reader.read_string(),
            public_key=reader.read_byte_array(),
            verify_token=reader.read_byte_array(),
        )


@dataclass
class EncryptionResponsePacket(Packet):
    """Serverbound Encryption Response packet (0x01)."""

    packet_id: ClassVar[int] = 0x01
    state: ClassVar[ProtocolState] = ProtocolState.LOGIN
    is_serverbound: ClassVar[bool] = True
    name: ClassVar[str] = "encryption_response"

    shared_secret: bytes
    verify_token: bytes

    def write(self, writer: PacketWriter) -> None:
        writer.write_byte_array(self.shared_secret)
        writer.write_byte_array(self.verify_token)

    @classmethod
    def decode(cls, reader: PacketReader) -> EncryptionResponsePacket:
        return cls(
            shared_secret=reader.read_byte_array(),
            verify_token=reader.read_byte_array(),
        )


@dataclass
class LoginSuccessPacket(Packet):
    """Clientbound Login Success packet (0x02)."""

    packet_id: ClassVar[int] = 0x02
    state: ClassVar[ProtocolState] = ProtocolState.LOGIN
    is_serverbound: ClassVar[bool] = False
    name: ClassVar[str] = "login_success"

    player_uuid: uuid.UUID
    username: str
    properties: list[dict] = field(default_factory=list)

    def write(self, writer: PacketWriter) -> None:
        writer.write_uuid(self.player_uuid)
        writer.write_string(self.username)
        writer.write_varint(len(self.properties))
        for prop in self.properties:
            writer.write_string(prop["name"])
            writer.write_string(prop["value"])
            has_sig = "signature" in prop and prop["signature"] is not None
            writer.write_bool(has_sig)
            if has_sig:
                writer.write_string(prop["signature"])

    @classmethod
    def decode(cls, reader: PacketReader) -> LoginSuccessPacket:
        player_uuid = reader.read_uuid()
        username = reader.read_string()
        num_props = reader.read_varint()
        properties = []
        for _ in range(num_props):
            p_name = reader.read_string()
            p_val = reader.read_string()
            has_sig = reader.read_bool()
            p_sig = reader.read_string() if has_sig else None
            properties.append({"name": p_name, "value": p_val, "signature": p_sig})
        return cls(player_uuid=player_uuid, username=username, properties=properties)


@dataclass
class SetCompressionPacket(Packet):
    """Clientbound Set Compression packet (0x03)."""

    packet_id: ClassVar[int] = 0x03
    state: ClassVar[ProtocolState] = ProtocolState.LOGIN
    is_serverbound: ClassVar[bool] = False
    name: ClassVar[str] = "set_compression"

    threshold: int

    def write(self, writer: PacketWriter) -> None:
        writer.write_varint(self.threshold)

    @classmethod
    def decode(cls, reader: PacketReader) -> SetCompressionPacket:
        return cls(threshold=reader.read_varint())


@dataclass
class LoginAcknowledgedPacket(Packet):
    """Serverbound Login Acknowledged packet (0x03 in 1.20.2+)."""

    packet_id: ClassVar[int] = 0x03
    state: ClassVar[ProtocolState] = ProtocolState.LOGIN
    is_serverbound: ClassVar[bool] = True
    name: ClassVar[str] = "login_acknowledged"

    @classmethod
    def decode(cls, reader: PacketReader) -> LoginAcknowledgedPacket:
        return cls()
