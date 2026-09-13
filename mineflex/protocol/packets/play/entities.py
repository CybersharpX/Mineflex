"""Entity spawn, movement, and interaction play packets."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import ClassVar, Optional

from mineflex.constants import InteractType, ProtocolState
from mineflex.protocol.buffer import PacketReader, PacketWriter
from mineflex.protocol.registry import Packet
from mineflex.types import Vec3


@dataclass
class SpawnEntityPacket(Packet):
    """Clientbound Spawn Entity packet (0x00 in 1.20.1)."""

    packet_id: ClassVar[int] = 0x00
    state: ClassVar[ProtocolState] = ProtocolState.PLAY
    is_serverbound: ClassVar[bool] = False
    name: ClassVar[str] = "spawn_entity"

    entity_id: int
    entity_uuid: uuid.UUID
    entity_type: int
    x: float
    y: float
    z: float
    pitch: float
    yaw: float
    head_yaw: float
    data: int
    vel_x: int = 0
    vel_y: int = 0
    vel_z: int = 0

    def write(self, writer: PacketWriter) -> None:
        writer.write_varint(self.entity_id)
        writer.write_uuid(self.entity_uuid)
        writer.write_varint(self.entity_type)
        writer.write_double(self.x)
        writer.write_double(self.y)
        writer.write_double(self.z)
        writer.write_ubyte(int((self.pitch % 360) * 256 / 360))
        writer.write_ubyte(int((self.yaw % 360) * 256 / 360))
        writer.write_ubyte(int((self.head_yaw % 360) * 256 / 360))
        writer.write_varint(self.data)
        writer.write_short(self.vel_x)
        writer.write_short(self.vel_y)
        writer.write_short(self.vel_z)

    @classmethod
    def decode(cls, reader: PacketReader) -> SpawnEntityPacket:
        return cls(
            entity_id=reader.read_varint(),
            entity_uuid=reader.read_uuid(),
            entity_type=reader.read_varint(),
            x=reader.read_double(),
            y=reader.read_double(),
            z=reader.read_double(),
            pitch=(reader.read_ubyte() * 360.0) / 256.0,
            yaw=(reader.read_ubyte() * 360.0) / 256.0,
            head_yaw=(reader.read_ubyte() * 360.0) / 256.0,
            data=reader.read_varint(),
            vel_x=reader.read_short(),
            vel_y=reader.read_short(),
            vel_z=reader.read_short(),
        )


@dataclass
class UpdateEntityPositionPacket(Packet):
    """Clientbound Update Entity Position packet (0x2B in 1.20.1)."""

    packet_id: ClassVar[int] = 0x2B
    state: ClassVar[ProtocolState] = ProtocolState.PLAY
    is_serverbound: ClassVar[bool] = False
    name: ClassVar[str] = "update_entity_position"

    entity_id: int
    delta_x: int  # (x_new - x_old) * 4096
    delta_y: int
    delta_z: int
    on_ground: bool

    def write(self, writer: PacketWriter) -> None:
        writer.write_varint(self.entity_id)
        writer.write_short(self.delta_x)
        writer.write_short(self.delta_y)
        writer.write_short(self.delta_z)
        writer.write_bool(self.on_ground)

    @classmethod
    def decode(cls, reader: PacketReader) -> UpdateEntityPositionPacket:
        return cls(
            entity_id=reader.read_varint(),
            delta_x=reader.read_short(),
            delta_y=reader.read_short(),
            delta_z=reader.read_short(),
            on_ground=reader.read_bool(),
        )


@dataclass
class UpdateEntityPositionRotationPacket(Packet):
    """Clientbound Update Entity Position and Rotation packet (0x2C in 1.20.1)."""

    packet_id: ClassVar[int] = 0x2C
    state: ClassVar[ProtocolState] = ProtocolState.PLAY
    is_serverbound: ClassVar[bool] = False
    name: ClassVar[str] = "update_entity_position_rotation"

    entity_id: int
    delta_x: int
    delta_y: int
    delta_z: int
    yaw: float
    pitch: float
    on_ground: bool

    def write(self, writer: PacketWriter) -> None:
        writer.write_varint(self.entity_id)
        writer.write_short(self.delta_x)
        writer.write_short(self.delta_y)
        writer.write_short(self.delta_z)
        writer.write_ubyte(int((self.yaw % 360) * 256 / 360))
        writer.write_ubyte(int((self.pitch % 360) * 256 / 360))
        writer.write_bool(self.on_ground)

    @classmethod
    def decode(cls, reader: PacketReader) -> UpdateEntityPositionRotationPacket:
        return cls(
            entity_id=reader.read_varint(),
            delta_x=reader.read_short(),
            delta_y=reader.read_short(),
            delta_z=reader.read_short(),
            yaw=(reader.read_ubyte() * 360.0) / 256.0,
            pitch=(reader.read_ubyte() * 360.0) / 256.0,
            on_ground=reader.read_bool(),
        )


@dataclass
class UpdateEntityRotationPacket(Packet):
    """Clientbound Update Entity Rotation packet (0x2D in 1.20.1)."""

    packet_id: ClassVar[int] = 0x2D
    state: ClassVar[ProtocolState] = ProtocolState.PLAY
    is_serverbound: ClassVar[bool] = False
    name: ClassVar[str] = "update_entity_rotation"

    entity_id: int
    yaw: float
    pitch: float
    on_ground: bool

    def write(self, writer: PacketWriter) -> None:
        writer.write_varint(self.entity_id)
        writer.write_ubyte(int((self.yaw % 360) * 256 / 360))
        writer.write_ubyte(int((self.pitch % 360) * 256 / 360))
        writer.write_bool(self.on_ground)

    @classmethod
    def decode(cls, reader: PacketReader) -> UpdateEntityRotationPacket:
        return cls(
            entity_id=reader.read_varint(),
            yaw=(reader.read_ubyte() * 360.0) / 256.0,
            pitch=(reader.read_ubyte() * 360.0) / 256.0,
            on_ground=reader.read_bool(),
        )


@dataclass
class DestroyEntitiesPacket(Packet):
    """Clientbound Remove Entities packet (0x40 in 1.20.1)."""

    packet_id: ClassVar[int] = 0x40
    state: ClassVar[ProtocolState] = ProtocolState.PLAY
    is_serverbound: ClassVar[bool] = False
    name: ClassVar[str] = "destroy_entities"

    entity_ids: list[int] = field(default_factory=list)

    def write(self, writer: PacketWriter) -> None:
        writer.write_varint(len(self.entity_ids))
        for eid in self.entity_ids:
            writer.write_varint(eid)

    @classmethod
    def decode(cls, reader: PacketReader) -> DestroyEntitiesPacket:
        count = reader.read_varint()
        return cls(entity_ids=[reader.read_varint() for _ in range(count)])


@dataclass
class SetEntityVelocityPacket(Packet):
    """Clientbound Set Entity Velocity packet (0x52 in 1.20.1)."""

    packet_id: ClassVar[int] = 0x52
    state: ClassVar[ProtocolState] = ProtocolState.PLAY
    is_serverbound: ClassVar[bool] = False
    name: ClassVar[str] = "set_entity_velocity"

    entity_id: int
    vel_x: int  # 8000 = 1 block/sec
    vel_y: int
    vel_z: int

    def write(self, writer: PacketWriter) -> None:
        writer.write_varint(self.entity_id)
        writer.write_short(self.vel_x)
        writer.write_short(self.vel_y)
        writer.write_short(self.vel_z)

    @classmethod
    def decode(cls, reader: PacketReader) -> SetEntityVelocityPacket:
        return cls(
            entity_id=reader.read_varint(),
            vel_x=reader.read_short(),
            vel_y=reader.read_short(),
            vel_z=reader.read_short(),
        )


@dataclass
class InteractPacket(Packet):
    """Serverbound Interact / Attack Entity packet (0x10 in 1.20.1)."""

    packet_id: ClassVar[int] = 0x10
    state: ClassVar[ProtocolState] = ProtocolState.PLAY
    is_serverbound: ClassVar[bool] = True
    name: ClassVar[str] = "interact"

    entity_id: int
    interact_type: InteractType | int
    target_pos: Optional[Vec3] = None
    hand: int = 0
    sneaking: bool = False

    def write(self, writer: PacketWriter) -> None:
        writer.write_varint(self.entity_id)
        writer.write_varint(int(self.interact_type))
        if self.interact_type == InteractType.INTERACT_AT and self.target_pos is not None:
            writer.write_float(self.target_pos.x)
            writer.write_float(self.target_pos.y)
            writer.write_float(self.target_pos.z)
            writer.write_varint(self.hand)
        elif self.interact_type == InteractType.INTERACT:
            writer.write_varint(self.hand)
        writer.write_bool(self.sneaking)

    @classmethod
    def decode(cls, reader: PacketReader) -> InteractPacket:
        entity_id = reader.read_varint()
        itype = reader.read_varint()
        target_pos = None
        hand = 0
        if itype == InteractType.INTERACT_AT:
            target_pos = Vec3(reader.read_float(), reader.read_float(), reader.read_float())
            hand = reader.read_varint()
        elif itype == InteractType.INTERACT:
            hand = reader.read_varint()
        sneaking = reader.read_bool()
        return cls(
            entity_id=entity_id,
            interact_type=itype,
            target_pos=target_pos,
            hand=hand,
            sneaking=sneaking,
        )
