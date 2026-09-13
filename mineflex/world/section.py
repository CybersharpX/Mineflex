"""Chunk section representation with 1.20+ paletted container parsing."""

from __future__ import annotations

from mineflex.protocol.buffer import PacketReader


class ChunkSection:
    """16x16x16 sub-chunk section with paletted block states and biomes."""

    __slots__ = ("block_count", "_blocks", "_biomes")

    def __init__(self, block_count: int = 0) -> None:
        self.block_count = block_count
        self._blocks: list[int] = [0] * 4096  # 16*16*16 local block states
        self._biomes: list[int] = [0] * 64  # 4*4*4 biomes

    def get_block_state(self, x: int, y: int, z: int) -> int:
        """Get block state ID at local coordinates (0..15)."""
        idx = (y * 16 + z) * 16 + x
        return self._blocks[idx]

    def set_block_state(self, x: int, y: int, z: int, state_id: int) -> None:
        """Set block state ID at local coordinates (0..15)."""
        idx = (y * 16 + z) * 16 + x
        old_val = self._blocks[idx]
        self._blocks[idx] = state_id
        if old_val == 0 and state_id != 0:
            self.block_count += 1
        elif old_val != 0 and state_id == 0:
            self.block_count = max(0, self.block_count - 1)

    @classmethod
    def decode(cls, reader: PacketReader) -> ChunkSection:
        """Decode a chunk section from raw packet bytes."""
        block_count = reader.read_short()
        section = cls(block_count=block_count)

        # 1. Decode Block States Paletted Container
        section._blocks = cls._decode_paletted_container(
            reader, expected_count=4096, min_bits=4, direct_bits=15
        )

        # 2. Decode Biomes Paletted Container (4x4x4 = 64 biomes)
        section._biomes = cls._decode_paletted_container(
            reader, expected_count=64, min_bits=1, direct_bits=6
        )

        return section

    @classmethod
    def _decode_paletted_container(
        cls, reader: PacketReader, expected_count: int, min_bits: int, direct_bits: int
    ) -> list[int]:
        bpb = reader.read_ubyte()

        if bpb == 0:
            # Single-valued palette
            val = reader.read_varint()
            data_len = reader.read_varint()
            if data_len > 0:
                reader.read_bytes(data_len * 8)
            return [val] * expected_count

        if bpb < min_bits:
            bpb = min_bits

        if bpb < direct_bits:
            # Indirect palette
            palette_len = reader.read_varint()
            palette = [reader.read_varint() for _ in range(palette_len)]
        else:
            # Direct palette
            palette = []

        data_len = reader.read_varint()
        longs = [reader.read_long() for _ in range(data_len)]

        result = [0] * expected_count
        values_per_long = 64 // bpb
        mask = (1 << bpb) - 1

        for i in range(expected_count):
            long_idx = i // values_per_long
            if long_idx >= len(longs):
                break
            start_bit = (i % values_per_long) * bpb
            # Treat long as unsigned 64-bit int for bit shifts
            raw_long = longs[long_idx] & 0xFFFFFFFFFFFFFFFF
            entry_idx = (raw_long >> start_bit) & mask
            if palette:
                result[i] = palette[entry_idx] if entry_idx < len(palette) else 0
            else:
                result[i] = entry_idx

        return result
