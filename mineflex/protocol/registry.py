"""Protocol registry mapping packet IDs, states, and codecs across versions."""

from __future__ import annotations

from typing import ClassVar, Dict, Optional, Tuple, Type

from mineflex.constants import DEFAULT_PROTOCOL_VERSION, ProtocolState
from mineflex.errors import UnsupportedVersionError
from mineflex.protocol.buffer import PacketReader, PacketWriter


class Packet:
    """Base class for strongly typed packet definitions."""

    packet_id: ClassVar[int] = -1
    state: ClassVar[ProtocolState] = ProtocolState.PLAY
    is_serverbound: ClassVar[bool] = False
    name: ClassVar[str] = "Packet"

    def encode(self) -> bytes:
        writer = PacketWriter()
        self.write(writer)
        return writer.get_bytes()

    def write(self, writer: PacketWriter) -> None:
        pass

    @classmethod
    def decode(cls, reader: PacketReader) -> Packet:
        raise NotImplementedError

    def __repr__(self) -> str:
        attrs = {k: v for k, v in self.__dict__.items() if not k.startswith("_")}
        return f"{self.__class__.__name__}({attrs})"


class ProtocolRegistry:
    """Central registry maintaining packet codecs for a specific Minecraft protocol version."""

    def __init__(self, protocol_version: int = DEFAULT_PROTOCOL_VERSION) -> None:
        self.protocol_version = protocol_version
        # (state, is_serverbound, packet_id) -> Packet class
        self._packets_by_id: Dict[Tuple[ProtocolState, bool, int], Type[Packet]] = {}
        # (state, is_serverbound, name) -> Packet class
        self._packets_by_name: Dict[Tuple[ProtocolState, bool, str], Type[Packet]] = {}

    def register(self, packet_cls: Type[Packet]) -> None:
        """Register a packet class into this protocol registry."""
        key_id = (packet_cls.state, packet_cls.is_serverbound, packet_cls.packet_id)
        key_name = (packet_cls.state, packet_cls.is_serverbound, packet_cls.name)
        self._packets_by_id[key_id] = packet_cls
        self._packets_by_name[key_name] = packet_cls

    def get_by_id(
        self, state: ProtocolState, is_serverbound: bool, packet_id: int
    ) -> Optional[Type[Packet]]:
        return self._packets_by_id.get((state, is_serverbound, packet_id))

    def get_by_name(
        self, state: ProtocolState, is_serverbound: bool, name: str
    ) -> Optional[Type[Packet]]:
        return self._packets_by_name.get((state, is_serverbound, name))

    def decode_packet(
        self, state: ProtocolState, is_serverbound: bool, packet_id: int, payload: bytes
    ) -> Optional[Packet]:
        """Decode raw packet payload into a typed Packet instance, or None if unknown."""
        packet_cls = self.get_by_id(state, is_serverbound, packet_id)
        if packet_cls is None:
            return None
        reader = PacketReader(payload)
        return packet_cls.decode(reader)

    _REGISTRIES_BY_VERSION: ClassVar[Dict[int, ProtocolRegistry]] = {}

    @classmethod
    def for_version(cls, version: int | str = DEFAULT_PROTOCOL_VERSION) -> ProtocolRegistry:
        from mineflex.constants import SUPPORTED_VERSIONS

        proto_id = (
            SUPPORTED_VERSIONS.get(str(version), version) if isinstance(version, str) else version
        )
        if not isinstance(proto_id, int):
            raise UnsupportedVersionError(f"Unsupported protocol version: {version}")

        if proto_id not in cls._REGISTRIES_BY_VERSION:
            reg = cls(protocol_version=proto_id)
            from mineflex.protocol.packets import register_standard_packets

            register_standard_packets(reg)
            cls._REGISTRIES_BY_VERSION[proto_id] = reg

        return cls._REGISTRIES_BY_VERSION[proto_id]
