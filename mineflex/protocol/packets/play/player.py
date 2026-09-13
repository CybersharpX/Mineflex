"""Player state, movement, and status packets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from mineflex.constants import BlockFace, DiggingStatus, Hand, ProtocolState
from mineflex.protocol.buffer import PacketReader, PacketWriter
from mineflex.protocol.registry import Packet
from mineflex.types import Position, Vec3


@dataclass
class LoginPlayPacket(Packet):
    """Clientbound Login (Play) packet (0x28 in 1.20.1)."""

    packet_id: ClassVar[int] = 0x28
    state: ClassVar[ProtocolState] = ProtocolState.PLAY
    is_serverbound: ClassVar[bool] = False
    name: ClassVar[str] = "login_play"

    entity_id: int
    is_hardcore: bool
    gamemode: int
    dimension_type: str = "minecraft:overworld"
    dimension_name: str = "minecraft:overworld"

    def write(self, writer: PacketWriter) -> None:
        writer.write_int(self.entity_id)
        writer.write_bool(self.is_hardcore)
        writer.write_byte(self.gamemode)
        writer.write_byte(-1)  # Previous gamemode
        writer.write_varint(1)  # Dimension count
        writer.write_string(self.dimension_name)
        # Empty registry codec
        writer.write_nbt({})
        writer.write_string(self.dimension_type)
        writer.write_string(self.dimension_name)
        writer.write_long(0)  # Hashed seed
        writer.write_varint(20)  # Max players
        writer.write_varint(10)  # View distance
        writer.write_varint(10)  # Simulation distance
        writer.write_bool(False)  # Reduced debug info
        writer.write_bool(True)  # Enable respawn screen
        writer.write_bool(False)  # Is debug
        writer.write_bool(False)  # Is flat
        writer.write_bool(False)  # Has death location
        writer.write_varint(0)  # Portal cooldown

    @classmethod
    def decode(cls, reader: PacketReader) -> LoginPlayPacket:
        entity_id = reader.read_int()
        is_hardcore = reader.read_bool()
        gamemode = reader.read_byte()
        reader.read_byte()  # Previous gamemode
        num_dims = reader.read_varint()
        for _ in range(num_dims):
            reader.read_string()
        reader.read_nbt()  # Registry codec
        dimension_type = reader.read_string()
        dimension_name = reader.read_string()
        # Skip the rest if present
        if reader.remaining > 0:
            reader.read_remaining()
        return cls(
            entity_id=entity_id,
            is_hardcore=is_hardcore,
            gamemode=gamemode,
            dimension_type=dimension_type,
            dimension_name=dimension_name,
        )


@dataclass
class SynchronizePositionPacket(Packet):
    """Clientbound Synchronize Player Position packet (0x3E in 1.20.1)."""

    packet_id: ClassVar[int] = 0x3E
    state: ClassVar[ProtocolState] = ProtocolState.PLAY
    is_serverbound: ClassVar[bool] = False
    name: ClassVar[str] = "synchronize_position"

    x: float
    y: float
    z: float
    yaw: float
    pitch: float
    flags: int
    teleport_id: int

    def write(self, writer: PacketWriter) -> None:
        writer.write_double(self.x)
        writer.write_double(self.y)
        writer.write_double(self.z)
        writer.write_float(self.yaw)
        writer.write_float(self.pitch)
        writer.write_byte(self.flags)
        writer.write_varint(self.teleport_id)

    @classmethod
    def decode(cls, reader: PacketReader) -> SynchronizePositionPacket:
        return cls(
            x=reader.read_double(),
            y=reader.read_double(),
            z=reader.read_double(),
            yaw=reader.read_float(),
            pitch=reader.read_float(),
            flags=reader.read_byte(),
            teleport_id=reader.read_varint(),
        )


@dataclass
class ConfirmTeleportPacket(Packet):
    """Serverbound Confirm Teleportation packet (0x00 in 1.20.1)."""

    packet_id: ClassVar[int] = 0x00
    state: ClassVar[ProtocolState] = ProtocolState.PLAY
    is_serverbound: ClassVar[bool] = True
    name: ClassVar[str] = "confirm_teleport"

    teleport_id: int

    def write(self, writer: PacketWriter) -> None:
        writer.write_varint(self.teleport_id)

    @classmethod
    def decode(cls, reader: PacketReader) -> ConfirmTeleportPacket:
        return cls(teleport_id=reader.read_varint())


@dataclass
class ClientInformationPacket(Packet):
    """Serverbound Client Information packet (0x05 in 1.20.1)."""

    packet_id: ClassVar[int] = 0x05
    state: ClassVar[ProtocolState] = ProtocolState.PLAY
    is_serverbound: ClassVar[bool] = True
    name: ClassVar[str] = "client_information"

    locale: str = "en_US"
    view_distance: int = 10
    chat_mode: int = 0
    chat_colors: bool = True
    displayed_skin_parts: int = 0x7F
    main_hand: int = 1  # 1 = Right, 0 = Left
    text_filtering: bool = False
    allows_listing: bool = True

    def write(self, writer: PacketWriter) -> None:
        writer.write_string(self.locale)
        writer.write_byte(self.view_distance)
        writer.write_varint(self.chat_mode)
        writer.write_bool(self.chat_colors)
        writer.write_ubyte(self.displayed_skin_parts)
        writer.write_varint(self.main_hand)
        writer.write_bool(self.text_filtering)
        writer.write_bool(self.allows_listing)

    @classmethod
    def decode(cls, reader: PacketReader) -> ClientInformationPacket:
        return cls(
            locale=reader.read_string(),
            view_distance=reader.read_byte(),
            chat_mode=reader.read_varint(),
            chat_colors=reader.read_bool(),
            displayed_skin_parts=reader.read_ubyte(),
            main_hand=reader.read_varint(),
            text_filtering=reader.read_bool(),
            allows_listing=reader.read_bool(),
        )


@dataclass
class SetPlayerPositionPacket(Packet):
    """Serverbound Set Player Position packet (0x14 in 1.20.1)."""

    packet_id: ClassVar[int] = 0x14
    state: ClassVar[ProtocolState] = ProtocolState.PLAY
    is_serverbound: ClassVar[bool] = True
    name: ClassVar[str] = "set_player_position"

    x: float
    y: float
    z: float
    on_ground: bool

    def write(self, writer: PacketWriter) -> None:
        writer.write_double(self.x)
        writer.write_double(self.y)
        writer.write_double(self.z)
        writer.write_bool(self.on_ground)

    @classmethod
    def decode(cls, reader: PacketReader) -> SetPlayerPositionPacket:
        return cls(
            x=reader.read_double(),
            y=reader.read_double(),
            z=reader.read_double(),
            on_ground=reader.read_bool(),
        )


@dataclass
class SetPlayerPositionAndRotationPacket(Packet):
    """Serverbound Set Player Position and Rotation packet (0x15 in 1.20.1)."""

    packet_id: ClassVar[int] = 0x15
    state: ClassVar[ProtocolState] = ProtocolState.PLAY
    is_serverbound: ClassVar[bool] = True
    name: ClassVar[str] = "set_player_position_and_rotation"

    x: float
    y: float
    z: float
    yaw: float
    pitch: float
    on_ground: bool

    def write(self, writer: PacketWriter) -> None:
        writer.write_double(self.x)
        writer.write_double(self.y)
        writer.write_double(self.z)
        writer.write_float(self.yaw)
        writer.write_float(self.pitch)
        writer.write_bool(self.on_ground)

    @classmethod
    def decode(cls, reader: PacketReader) -> SetPlayerPositionAndRotationPacket:
        return cls(
            x=reader.read_double(),
            y=reader.read_double(),
            z=reader.read_double(),
            yaw=reader.read_float(),
            pitch=reader.read_float(),
            on_ground=reader.read_bool(),
        )


@dataclass
class SetPlayerRotationPacket(Packet):
    """Serverbound Set Player Rotation packet (0x16 in 1.20.1)."""

    packet_id: ClassVar[int] = 0x16
    state: ClassVar[ProtocolState] = ProtocolState.PLAY
    is_serverbound: ClassVar[bool] = True
    name: ClassVar[str] = "set_player_rotation"

    yaw: float
    pitch: float
    on_ground: bool

    def write(self, writer: PacketWriter) -> None:
        writer.write_float(self.yaw)
        writer.write_float(self.pitch)
        writer.write_bool(self.on_ground)

    @classmethod
    def decode(cls, reader: PacketReader) -> SetPlayerRotationPacket:
        return cls(
            yaw=reader.read_float(),
            pitch=reader.read_float(),
            on_ground=reader.read_bool(),
        )


@dataclass
class SetPlayerOnGroundPacket(Packet):
    """Serverbound Set Player On Ground packet (0x17 in 1.20.1)."""

    packet_id: ClassVar[int] = 0x17
    state: ClassVar[ProtocolState] = ProtocolState.PLAY
    is_serverbound: ClassVar[bool] = True
    name: ClassVar[str] = "set_player_on_ground"

    on_ground: bool

    def write(self, writer: PacketWriter) -> None:
        writer.write_bool(self.on_ground)

    @classmethod
    def decode(cls, reader: PacketReader) -> SetPlayerOnGroundPacket:
        return cls(on_ground=reader.read_bool())


@dataclass
class PlayerActionPacket(Packet):
    """Serverbound Player Action packet (Digging/item drop) (0x1B in 1.20.1)."""

    packet_id: ClassVar[int] = 0x1B
    state: ClassVar[ProtocolState] = ProtocolState.PLAY
    is_serverbound: ClassVar[bool] = True
    name: ClassVar[str] = "player_action"

    status: DiggingStatus | int
    pos: Position | Vec3
    face: BlockFace | int
    sequence: int = 0

    def write(self, writer: PacketWriter) -> None:
        writer.write_varint(int(self.status))
        pos = self.pos if isinstance(self.pos, Position) else Position.from_vec3(self.pos)
        writer.write_position(pos)
        writer.write_byte(int(self.face))
        writer.write_varint(self.sequence)

    @classmethod
    def decode(cls, reader: PacketReader) -> PlayerActionPacket:
        return cls(
            status=reader.read_varint(),
            pos=reader.read_position(),
            face=reader.read_byte(),
            sequence=reader.read_varint(),
        )


@dataclass
class SwingArmPacket(Packet):
    """Serverbound Swing Arm packet (0x30 in 1.20.1)."""

    packet_id: ClassVar[int] = 0x30
    state: ClassVar[ProtocolState] = ProtocolState.PLAY
    is_serverbound: ClassVar[bool] = True
    name: ClassVar[str] = "swing_arm"

    hand: Hand | int = Hand.MAIN_HAND

    def write(self, writer: PacketWriter) -> None:
        writer.write_varint(int(self.hand))

    @classmethod
    def decode(cls, reader: PacketReader) -> SwingArmPacket:
        return cls(hand=reader.read_varint())


@dataclass
class UseItemOnPacket(Packet):
    """Serverbound Use Item On / Place Block packet (0x31 in 1.20.1)."""

    packet_id: ClassVar[int] = 0x31
    state: ClassVar[ProtocolState] = ProtocolState.PLAY
    is_serverbound: ClassVar[bool] = True
    name: ClassVar[str] = "use_item_on"

    hand: Hand | int
    pos: Position | Vec3
    face: BlockFace | int
    cursor_x: float = 0.5
    cursor_y: float = 0.5
    cursor_z: float = 0.5
    inside_block: bool = False
    sequence: int = 0

    def write(self, writer: PacketWriter) -> None:
        writer.write_varint(int(self.hand))
        pos = self.pos if isinstance(self.pos, Position) else Position.from_vec3(self.pos)
        writer.write_position(pos)
        writer.write_varint(int(self.face))
        writer.write_float(self.cursor_x)
        writer.write_float(self.cursor_y)
        writer.write_float(self.cursor_z)
        writer.write_bool(self.inside_block)
        writer.write_varint(self.sequence)

    @classmethod
    def decode(cls, reader: PacketReader) -> UseItemOnPacket:
        return cls(
            hand=reader.read_varint(),
            pos=reader.read_position(),
            face=reader.read_varint(),
            cursor_x=reader.read_float(),
            cursor_y=reader.read_float(),
            cursor_z=reader.read_float(),
            inside_block=reader.read_bool(),
            sequence=reader.read_varint(),
        )


@dataclass
class UseItemPacket(Packet):
    """Serverbound Use Item packet (0x32 in 1.20.1)."""

    packet_id: ClassVar[int] = 0x32
    state: ClassVar[ProtocolState] = ProtocolState.PLAY
    is_serverbound: ClassVar[bool] = True
    name: ClassVar[str] = "use_item"

    hand: Hand | int
    sequence: int = 0

    def write(self, writer: PacketWriter) -> None:
        writer.write_varint(int(self.hand))
        writer.write_varint(self.sequence)

    @classmethod
    def decode(cls, reader: PacketReader) -> UseItemPacket:
        return cls(hand=reader.read_varint(), sequence=reader.read_varint())


@dataclass
class SetHealthPacket(Packet):
    """Clientbound Set Health packet (0x55 in 1.20.1)."""

    packet_id: ClassVar[int] = 0x55
    state: ClassVar[ProtocolState] = ProtocolState.PLAY
    is_serverbound: ClassVar[bool] = False
    name: ClassVar[str] = "set_health"

    health: float
    food: int
    food_saturation: float

    def write(self, writer: PacketWriter) -> None:
        writer.write_float(self.health)
        writer.write_varint(self.food)
        writer.write_float(self.food_saturation)

    @classmethod
    def decode(cls, reader: PacketReader) -> SetHealthPacket:
        return cls(
            health=reader.read_float(),
            food=reader.read_varint(),
            food_saturation=reader.read_float(),
        )


@dataclass
class SetExperiencePacket(Packet):
    """Clientbound Set Experience packet (0x58 in 1.20.1)."""

    packet_id: ClassVar[int] = 0x58
    state: ClassVar[ProtocolState] = ProtocolState.PLAY
    is_serverbound: ClassVar[bool] = False
    name: ClassVar[str] = "set_experience"

    experience_bar: float
    level: int
    total_experience: int

    def write(self, writer: PacketWriter) -> None:
        writer.write_float(self.experience_bar)
        writer.write_varint(self.level)
        writer.write_varint(self.total_experience)

    @classmethod
    def decode(cls, reader: PacketReader) -> SetExperiencePacket:
        return cls(
            experience_bar=reader.read_float(),
            level=reader.read_varint(),
            total_experience=reader.read_varint(),
        )


@dataclass
class UpdateTimePacket(Packet):
    """Clientbound Update Time packet (0x5C in 1.20.1)."""

    packet_id: ClassVar[int] = 0x5C
    state: ClassVar[ProtocolState] = ProtocolState.PLAY
    is_serverbound: ClassVar[bool] = False
    name: ClassVar[str] = "update_time"

    world_age: int
    time_of_day: int

    def write(self, writer: PacketWriter) -> None:
        writer.write_long(self.world_age)
        writer.write_long(self.time_of_day)

    @classmethod
    def decode(cls, reader: PacketReader) -> UpdateTimePacket:
        return cls(world_age=reader.read_long(), time_of_day=reader.read_long())
