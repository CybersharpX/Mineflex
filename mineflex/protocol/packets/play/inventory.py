"""Inventory, window, and container play packets."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar, Optional

from mineflex.constants import ProtocolState
from mineflex.protocol.buffer import PacketReader, PacketWriter
from mineflex.protocol.registry import Packet


@dataclass
class SetContainerContentPacket(Packet):
    """Clientbound Set Container Content (Window Items) packet (0x11 in 1.20.1)."""

    packet_id: ClassVar[int] = 0x11
    state: ClassVar[ProtocolState] = ProtocolState.PLAY
    is_serverbound: ClassVar[bool] = False
    name: ClassVar[str] = "set_container_content"

    window_id: int
    state_id: int
    items: list[Optional[dict[str, Any]]] = field(default_factory=list)
    carried_item: Optional[dict[str, Any]] = None

    def write(self, writer: PacketWriter) -> None:
        writer.write_ubyte(self.window_id)
        writer.write_varint(self.state_id)
        writer.write_varint(len(self.items))
        for item in self.items:
            writer.write_slot(item)
        writer.write_slot(self.carried_item)

    @classmethod
    def decode(cls, reader: PacketReader) -> SetContainerContentPacket:
        window_id = reader.read_ubyte()
        state_id = reader.read_varint()
        count = reader.read_varint()
        items = [reader.read_slot() for _ in range(count)]
        carried_item = reader.read_slot()
        return cls(
            window_id=window_id,
            state_id=state_id,
            items=items,
            carried_item=carried_item,
        )


@dataclass
class SetContainerSlotPacket(Packet):
    """Clientbound Set Container Slot packet (0x13 in 1.20.1)."""

    packet_id: ClassVar[int] = 0x13
    state: ClassVar[ProtocolState] = ProtocolState.PLAY
    is_serverbound: ClassVar[bool] = False
    name: ClassVar[str] = "set_container_slot"

    window_id: int
    state_id: int
    slot: int
    item: Optional[dict[str, Any]] = None

    def write(self, writer: PacketWriter) -> None:
        writer.write_byte(self.window_id)
        writer.write_varint(self.state_id)
        writer.write_short(self.slot)
        writer.write_slot(self.item)

    @classmethod
    def decode(cls, reader: PacketReader) -> SetContainerSlotPacket:
        return cls(
            window_id=reader.read_byte(),
            state_id=reader.read_varint(),
            slot=reader.read_short(),
            item=reader.read_slot(),
        )


@dataclass
class OpenScreenPacket(Packet):
    """Clientbound Open Screen packet (0x10 in 1.20.1)."""

    packet_id: ClassVar[int] = 0x10
    state: ClassVar[ProtocolState] = ProtocolState.PLAY
    is_serverbound: ClassVar[bool] = False
    name: ClassVar[str] = "open_screen"

    window_id: int
    window_type: int
    title: str

    def write(self, writer: PacketWriter) -> None:
        writer.write_varint(self.window_id)
        writer.write_varint(self.window_type)
        writer.write_string(self.title)

    @classmethod
    def decode(cls, reader: PacketReader) -> OpenScreenPacket:
        return cls(
            window_id=reader.read_varint(),
            window_type=reader.read_varint(),
            title=reader.read_string(),
        )


@dataclass
class CloseContainerClientboundPacket(Packet):
    """Clientbound Close Container packet (0x12 in 1.20.1)."""

    packet_id: ClassVar[int] = 0x12
    state: ClassVar[ProtocolState] = ProtocolState.PLAY
    is_serverbound: ClassVar[bool] = False
    name: ClassVar[str] = "close_container_clientbound"

    window_id: int

    def write(self, writer: PacketWriter) -> None:
        writer.write_ubyte(self.window_id)

    @classmethod
    def decode(cls, reader: PacketReader) -> CloseContainerClientboundPacket:
        return cls(window_id=reader.read_ubyte())


@dataclass
class ClickContainerPacket(Packet):
    """Serverbound Click Container packet (0x09 in 1.20.1)."""

    packet_id: ClassVar[int] = 0x09
    state: ClassVar[ProtocolState] = ProtocolState.PLAY
    is_serverbound: ClassVar[bool] = True
    name: ClassVar[str] = "click_container"

    window_id: int
    state_id: int
    slot: int
    button: int
    mode: int
    changed_slots: dict[int, Optional[dict[str, Any]]] = field(default_factory=dict)
    carried_item: Optional[dict[str, Any]] = None

    def write(self, writer: PacketWriter) -> None:
        writer.write_byte(self.window_id)
        writer.write_varint(self.state_id)
        writer.write_short(self.slot)
        writer.write_byte(self.button)
        writer.write_varint(self.mode)
        writer.write_varint(len(self.changed_slots))
        for s_idx, s_item in self.changed_slots.items():
            writer.write_short(s_idx)
            writer.write_slot(s_item)
        writer.write_slot(self.carried_item)

    @classmethod
    def decode(cls, reader: PacketReader) -> ClickContainerPacket:
        window_id = reader.read_byte()
        state_id = reader.read_varint()
        slot = reader.read_short()
        button = reader.read_byte()
        mode = reader.read_varint()
        num_changed = reader.read_varint()
        changed_slots = {}
        for _ in range(num_changed):
            s_idx = reader.read_short()
            s_item = reader.read_slot()
            changed_slots[s_idx] = s_item
        carried_item = reader.read_slot()
        return cls(
            window_id=window_id,
            state_id=state_id,
            slot=slot,
            button=button,
            mode=mode,
            changed_slots=changed_slots,
            carried_item=carried_item,
        )


@dataclass
class CloseContainerServerboundPacket(Packet):
    """Serverbound Close Container packet (0x0B in 1.20.1)."""

    packet_id: ClassVar[int] = 0x0B
    state: ClassVar[ProtocolState] = ProtocolState.PLAY
    is_serverbound: ClassVar[bool] = True
    name: ClassVar[str] = "close_container_serverbound"

    window_id: int

    def write(self, writer: PacketWriter) -> None:
        writer.write_byte(self.window_id)

    @classmethod
    def decode(cls, reader: PacketReader) -> CloseContainerServerboundPacket:
        return cls(window_id=reader.read_byte())


@dataclass
class SetHeldItemPacket(Packet):
    """Serverbound Set Held Item packet (0x25 in 1.20.1)."""

    packet_id: ClassVar[int] = 0x25
    state: ClassVar[ProtocolState] = ProtocolState.PLAY
    is_serverbound: ClassVar[bool] = True
    name: ClassVar[str] = "set_held_item"

    slot: int  # 0-8

    def write(self, writer: PacketWriter) -> None:
        writer.write_short(self.slot)

    @classmethod
    def decode(cls, reader: PacketReader) -> SetHeldItemPacket:
        return cls(slot=reader.read_short())
