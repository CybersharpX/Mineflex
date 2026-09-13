"""Packet framing, serialization, and stream decoding for the Minecraft protocol."""

from __future__ import annotations

import asyncio
import zlib
from typing import Tuple

from mineflex.errors import ConnectionError, PacketError
from mineflex.protocol.buffer import PacketReader, PacketWriter


class PacketFramer:
    """Handles framing, deframing, compression, and decompression of packets."""

    def __init__(self, compression_threshold: int = -1) -> None:
        self.compression_threshold = compression_threshold

    def set_compression_threshold(self, threshold: int) -> None:
        self.compression_threshold = threshold

    def frame_packet(self, packet_id: int, payload: bytes) -> bytes:
        """Encode packet ID and payload into a wire-ready framed byte sequence."""
        id_writer = PacketWriter()
        id_writer.write_varint(packet_id)
        raw_packet = id_writer.get_bytes() + payload

        if self.compression_threshold >= 0:
            frame_writer = PacketWriter()
            if len(raw_packet) >= self.compression_threshold:
                compressed = zlib.compress(raw_packet)
                frame_writer.write_varint(len(raw_packet))
                frame_writer.write_bytes(compressed)
            else:
                frame_writer.write_varint(0)
                frame_writer.write_bytes(raw_packet)
            frame_body = frame_writer.get_bytes()
        else:
            frame_body = raw_packet

        length_writer = PacketWriter()
        length_writer.write_varint(len(frame_body))
        return length_writer.get_bytes() + frame_body

    async def read_packet_frame(self, reader: asyncio.StreamReader) -> Tuple[int, bytes]:
        """Read a single complete packet frame from an asyncio StreamReader."""
        # Read frame length VarInt
        length = await self._read_varint_from_stream(reader)
        if length <= 0 or length > 2097152:  # Max 2MB packet
            raise PacketError(f"Invalid frame length: {length}")

        try:
            frame_data = await reader.readexactly(length)
        except asyncio.IncompleteReadError as exc:
            raise ConnectionError("Connection closed while reading packet frame") from exc

        if self.compression_threshold >= 0:
            buffer_reader = PacketReader(frame_data)
            data_length = buffer_reader.read_varint()
            compressed_payload = buffer_reader.read_remaining()

            if data_length == 0:
                # Uncompressed under threshold
                packet_reader = PacketReader(compressed_payload)
            else:
                # Compressed payload
                try:
                    decompressed = zlib.decompress(compressed_payload)
                except zlib.error as exc:
                    raise PacketError(f"Zlib decompression failed: {exc}") from exc
                if len(decompressed) != data_length:
                    raise PacketError(
                        f"Decompressed length mismatch: expected {data_length}, "
                        f"got {len(decompressed)}"
                    )
                packet_reader = PacketReader(decompressed)
        else:
            packet_reader = PacketReader(frame_data)

        packet_id = packet_reader.read_varint()
        payload = packet_reader.read_remaining()
        return packet_id, payload

    @staticmethod
    async def _read_varint_from_stream(reader: asyncio.StreamReader) -> int:
        value = 0
        position = 0

        while True:
            try:
                byte_data = await reader.readexactly(1)
            except asyncio.IncompleteReadError as exc:
                raise ConnectionError("Connection closed while reading packet frame") from exc

            byte = byte_data[0]
            value |= (byte & 0x7F) << position
            if (byte & 0x80) == 0:
                break
            position += 7
            if position >= 35:
                raise PacketError("VarInt in stream framing is too wide")

        if value & (1 << 31):
            value -= 1 << 32
        return value
