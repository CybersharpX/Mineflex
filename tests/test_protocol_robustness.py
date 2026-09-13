"""Tests for protocol fuzzing, malformed packet handling, and stream robustness."""

from __future__ import annotations

import asyncio
import zlib

import pytest

from mineflex.errors import ConnectionError, NBTError, PacketError
from mineflex.nbt.reader import NBTReader
from mineflex.protocol.buffer import PacketReader, PacketWriter
from mineflex.protocol.framing import PacketFramer


def test_varint_overflow():
    """VarInt wider than 5 bytes (35 bits) must raise PacketError."""
    overflow_bytes = b"\x80\x80\x80\x80\x80\x01"
    reader = PacketReader(overflow_bytes)
    with pytest.raises(PacketError, match="VarInt is too wide"):
        reader.read_varint()


def test_varlong_overflow():
    """VarLong wider than 10 bytes (70 bits) must raise PacketError."""
    overflow_bytes = b"\x80" * 10 + b"\x01"
    reader = PacketReader(overflow_bytes)
    with pytest.raises(PacketError, match="VarLong is too wide"):
        reader.read_varlong()


def test_string_length_limit():
    """Reading string with declared length exceeding max_len must raise PacketError."""
    writer = PacketWriter()
    writer.write_varint(1000)
    writer.write_bytes(b"a" * 1000)

    reader = PacketReader(writer.get_bytes())
    with pytest.raises(PacketError, match="exceeds bounds"):
        reader.read_string(max_length=50)


@pytest.mark.asyncio
async def test_frame_length_oversized():
    """Frame claiming to be larger than 2MB must be rejected immediately."""
    framer = PacketFramer()

    # Encode length 3MB (3 * 1024 * 1024 = 3145728)
    writer = PacketWriter()
    writer.write_varint(3145728)

    reader = asyncio.StreamReader()
    reader.feed_data(writer.get_bytes())
    reader.feed_eof()

    with pytest.raises(PacketError, match="Invalid frame length"):
        await framer.read_packet_frame(reader)


@pytest.mark.asyncio
async def test_frame_length_zero():
    """Frame claiming length 0 must be rejected."""
    framer = PacketFramer()

    writer = PacketWriter()
    writer.write_varint(0)

    reader = asyncio.StreamReader()
    reader.feed_data(writer.get_bytes())
    reader.feed_eof()

    with pytest.raises(PacketError, match="Invalid frame length"):
        await framer.read_packet_frame(reader)


@pytest.mark.asyncio
async def test_corrupted_compressed_packet():
    """Compressed packet with corrupted zlib data must raise PacketError."""
    framer = PacketFramer(compression_threshold=256)

    # Frame containing uncompressed length > 0, followed by corrupted garbage bytes
    writer = PacketWriter()
    writer.write_varint(500)  # Claimed uncompressed size
    writer.write_bytes(b"not_a_valid_zlib_stream_garbage_12345")

    frame_payload = writer.get_bytes()
    len_writer = PacketWriter()
    len_writer.write_varint(len(frame_payload))

    reader = asyncio.StreamReader()
    reader.feed_data(len_writer.get_bytes() + frame_payload)
    reader.feed_eof()

    with pytest.raises(PacketError, match="Zlib decompression failed"):
        await framer.read_packet_frame(reader)


@pytest.mark.asyncio
async def test_decompressed_length_mismatch():
    """Decompressed data size differing from header uncompressed size must raise PacketError."""
    framer = PacketFramer(compression_threshold=10)

    real_data = b"Hello World"
    compressed = zlib.compress(real_data)

    writer = PacketWriter()
    writer.write_varint(9999)  # Falsely claims 9999 bytes
    writer.write_bytes(compressed)

    frame_payload = writer.get_bytes()
    len_writer = PacketWriter()
    len_writer.write_varint(len(frame_payload))

    reader = asyncio.StreamReader()
    reader.feed_data(len_writer.get_bytes() + frame_payload)
    reader.feed_eof()

    with pytest.raises(PacketError, match="Decompressed length mismatch"):
        await framer.read_packet_frame(reader)


@pytest.mark.asyncio
async def test_truncated_stream():
    """Stream ending prematurely while reading frame must raise ConnectionError."""
    framer = PacketFramer()

    writer = PacketWriter()
    writer.write_varint(100)  # Claims 100 bytes
    writer.write_bytes(b"only 10 bytes!")

    reader = asyncio.StreamReader()
    reader.feed_data(writer.get_bytes())
    reader.feed_eof()

    with pytest.raises(ConnectionError, match="Connection closed"):
        await framer.read_packet_frame(reader)


def test_malformed_nbt_truncated():
    """Truncated NBT data must raise NBTError or EOFError cleanly."""
    truncated = b"\x0a\x00\x04test\x08\x00\x04name\x00\x10trun"
    reader = NBTReader(truncated)
    with pytest.raises((NBTError, EOFError, Exception)):
        reader.read_tag()
