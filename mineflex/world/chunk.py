"""Chunk column container managing 24 vertical chunk sections."""

from __future__ import annotations

from typing import Dict, Optional

from mineflex.protocol.buffer import PacketReader
from mineflex.world.section import ChunkSection


class Chunk:
    """A 16x16 vertical chunk column spanning from Y=-64 to Y=320 (24 sections)."""

    SECTION_COUNT = 24
    MIN_Y = -64
    MAX_Y = 320

    def __init__(self, chunk_x: int, chunk_z: int) -> None:
        self.chunk_x = chunk_x
        self.chunk_z = chunk_z
        self.sections: Dict[int, ChunkSection] = {
            i: ChunkSection() for i in range(self.SECTION_COUNT)
        }
        self.block_entities: dict[tuple[int, int, int], dict] = {}

    def get_section_index(self, y: int) -> Optional[int]:
        if y < self.MIN_Y or y >= self.MAX_Y:
            return None
        return (y - self.MIN_Y) >> 4

    def get_block_state(self, x: int, y: int, z: int) -> int:
        """Get the block state ID at local chunk coordinates (x: 0..15, y: -64..319, z: 0..15)."""
        sec_idx = self.get_section_index(y)
        if sec_idx is None:
            return 0
        section = self.sections.get(sec_idx)
        if section is None:
            return 0
        local_y = (y - self.MIN_Y) & 0xF
        return section.get_block_state(x & 0xF, local_y, z & 0xF)

    def set_block_state(self, x: int, y: int, z: int, state_id: int) -> None:
        """Set the block state ID at local chunk coordinates."""
        sec_idx = self.get_section_index(y)
        if sec_idx is None:
            return
        if sec_idx not in self.sections:
            self.sections[sec_idx] = ChunkSection()
        local_y = (y - self.MIN_Y) & 0xF
        self.sections[sec_idx].set_block_state(x & 0xF, local_y, z & 0xF, state_id)

    def load_data(self, data: bytes) -> None:
        """Decode all 24 chunk sections from raw packet data."""
        reader = PacketReader(data)
        for i in range(self.SECTION_COUNT):
            if reader.remaining == 0:
                break
            self.sections[i] = ChunkSection.decode(reader)
