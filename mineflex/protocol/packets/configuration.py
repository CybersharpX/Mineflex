"""Configuration state packets for Minecraft 1.20.2+ (Protocols 764, 765, 767)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar, List, Tuple

from mineflex.constants import ProtocolState
from mineflex.protocol.buffer import PacketReader, PacketWriter
from mineflex.protocol.registry import Packet


@dataclass
class FinishConfigurationClientboundPacket(Packet):
    """Clientbound Finish Configuration packet (0x02 in CONFIGURATION state)."""

    packet_id: ClassVar[int] = 0x02
    state: ClassVar[ProtocolState] = ProtocolState.CONFIGURATION
    is_serverbound: ClassVar[bool] = False
    name: ClassVar[str] = "finish_configuration"

    def write(self, writer: PacketWriter) -> None:
        pass

    @classmethod
    def decode(cls, reader: PacketReader) -> FinishConfigurationClientboundPacket:
        return cls()


@dataclass
class FinishConfigurationServerboundPacket(Packet):
    """Serverbound Acknowledge Finish Configuration packet (0x02 in CONFIGURATION state)."""

    packet_id: ClassVar[int] = 0x02
    state: ClassVar[ProtocolState] = ProtocolState.CONFIGURATION
    is_serverbound: ClassVar[bool] = True
    name: ClassVar[str] = "finish_configuration_ack"

    def write(self, writer: PacketWriter) -> None:
        pass

    @classmethod
    def decode(cls, reader: PacketReader) -> FinishConfigurationServerboundPacket:
        return cls()


@dataclass
class RegistryDataPacket(Packet):
    """Clientbound Registry Data packet (0x05 in CONFIGURATION state)."""

    packet_id: ClassVar[int] = 0x05
    state: ClassVar[ProtocolState] = ProtocolState.CONFIGURATION
    is_serverbound: ClassVar[bool] = False
    name: ClassVar[str] = "registry_data"

    registry_id: str
    entry_count: int = 0

    def write(self, writer: PacketWriter) -> None:
        writer.write_string(self.registry_id)
        writer.write_varint(self.entry_count)

    @classmethod
    def decode(cls, reader: PacketReader) -> RegistryDataPacket:
        reg_id = reader.read_string()
        count = reader.read_varint()
        return cls(registry_id=reg_id, entry_count=count)


@dataclass
class FeatureFlagsPacket(Packet):
    """Clientbound Feature Flags packet (0x08 in CONFIGURATION state)."""

    packet_id: ClassVar[int] = 0x08
    state: ClassVar[ProtocolState] = ProtocolState.CONFIGURATION
    is_serverbound: ClassVar[bool] = False
    name: ClassVar[str] = "feature_flags"

    features: List[str] = field(default_factory=list)

    def write(self, writer: PacketWriter) -> None:
        writer.write_varint(len(self.features))
        for f in self.features:
            writer.write_string(f)

    @classmethod
    def decode(cls, reader: PacketReader) -> FeatureFlagsPacket:
        count = reader.read_varint()
        features = [reader.read_string() for _ in range(count)]
        return cls(features=features)


@dataclass
class KnownPacksPacket(Packet):
    """Clientbound Known Packs packet (0x0E in CONFIGURATION state)."""

    packet_id: ClassVar[int] = 0x0E
    state: ClassVar[ProtocolState] = ProtocolState.CONFIGURATION
    is_serverbound: ClassVar[bool] = False
    name: ClassVar[str] = "known_packs"

    packs: List[Tuple[str, str, str]] = field(default_factory=list)

    def write(self, writer: PacketWriter) -> None:
        writer.write_varint(len(self.packs))
        for namespace, pack_id, version in self.packs:
            writer.write_string(namespace)
            writer.write_string(pack_id)
            writer.write_string(version)

    @classmethod
    def decode(cls, reader: PacketReader) -> KnownPacksPacket:
        count = reader.read_varint()
        packs = []
        for _ in range(count):
            namespace = reader.read_string()
            pack_id = reader.read_string()
            version = reader.read_string()
            packs.append((namespace, pack_id, version))
        return cls(packs=packs)


@dataclass
class KeepAliveConfigurationClientboundPacket(Packet):
    """Clientbound Keep Alive (Configuration) packet (0x04 in CONFIGURATION state)."""

    packet_id: ClassVar[int] = 0x04
    state: ClassVar[ProtocolState] = ProtocolState.CONFIGURATION
    is_serverbound: ClassVar[bool] = False
    name: ClassVar[str] = "keep_alive_config"

    keep_alive_id: int

    def write(self, writer: PacketWriter) -> None:
        writer.write_long(self.keep_alive_id)

    @classmethod
    def decode(cls, reader: PacketReader) -> KeepAliveConfigurationClientboundPacket:
        return cls(keep_alive_id=reader.read_long())


@dataclass
class KeepAliveConfigurationServerboundPacket(Packet):
    """Serverbound Keep Alive (Configuration) packet (0x04 in CONFIGURATION state)."""

    packet_id: ClassVar[int] = 0x04
    state: ClassVar[ProtocolState] = ProtocolState.CONFIGURATION
    is_serverbound: ClassVar[bool] = True
    name: ClassVar[str] = "keep_alive_config_ack"

    keep_alive_id: int

    def write(self, writer: PacketWriter) -> None:
        writer.write_long(self.keep_alive_id)

    @classmethod
    def decode(cls, reader: PacketReader) -> KeepAliveConfigurationServerboundPacket:
        return cls(keep_alive_id=reader.read_long())


@dataclass
class DisconnectConfigurationPacket(Packet):
    """Clientbound Disconnect (Configuration) packet (0x01 in CONFIGURATION state)."""

    packet_id: ClassVar[int] = 0x01
    state: ClassVar[ProtocolState] = ProtocolState.CONFIGURATION
    is_serverbound: ClassVar[bool] = False
    name: ClassVar[str] = "disconnect_config"

    reason: str

    def write(self, writer: PacketWriter) -> None:
        writer.write_string(self.reason)

    @classmethod
    def decode(cls, reader: PacketReader) -> DisconnectConfigurationPacket:
        return cls(reason=reader.read_string())
