"""Unit tests for protocol buffer, framing, encryption, and packet codecs."""

import asyncio
import os
import uuid

import pytest

from mineflex.constants import DEFAULT_PROTOCOL_VERSION, ProtocolState
from mineflex.protocol.buffer import PacketReader, PacketWriter
from mineflex.protocol.encryption import EncryptionCipher
from mineflex.protocol.framing import PacketFramer
from mineflex.protocol.packets.handshake import HandshakePacket
from mineflex.protocol.packets.login import (
    LoginStartPacket,
)
from mineflex.protocol.packets.play.player import (
    SynchronizePositionPacket,
)
from mineflex.protocol.registry import ProtocolRegistry
from mineflex.types import Position


@pytest.mark.parametrize(
    "value, expected_bytes",
    [
        (0, b"\x00"),
        (1, b"\x01"),
        (2, b"\x02"),
        (127, b"\x7f"),
        (128, b"\x80\x01"),
        (255, b"\xff\x01"),
        (25565, b"\xdd\xc7\x01"),
        (2097151, b"\xff\xff\x7f"),
        (2147483647, b"\xff\xff\xff\xff\x07"),
        (-1, b"\xff\xff\xff\xff\x0f"),
        (-2147483648, b"\x80\x80\x80\x80\x08"),
    ],
)
def test_varint_roundtrip(value, expected_bytes):
    writer = PacketWriter()
    writer.write_varint(value)
    data = writer.get_bytes()
    assert data == expected_bytes

    reader = PacketReader(data)
    decoded = reader.read_varint()
    assert decoded == value
    assert reader.remaining == 0


def test_varlong_roundtrip():
    test_values = [0, 1, 127, 128, 2147483647, 9223372036854775807, -1, -9223372036854775808]
    for val in test_values:
        writer = PacketWriter()
        writer.write_varlong(val)
        data = writer.get_bytes()
        reader = PacketReader(data)
        assert reader.read_varlong() == val
        assert reader.remaining == 0


def test_primitive_codecs():
    writer = PacketWriter()
    test_uuid = uuid.uuid4()
    test_pos = Position(100, 64, -200)

    writer.write_bool(True)
    writer.write_byte(-5)
    writer.write_ubyte(250)
    writer.write_short(-1234)
    writer.write_ushort(50000)
    writer.write_int(-987654)
    writer.write_long(1234567890123)
    writer.write_float(3.14159)
    writer.write_double(2.718281828)
    writer.write_string("Hello Minecraft")
    writer.write_uuid(test_uuid)
    writer.write_position(test_pos)

    reader = PacketReader(writer.get_bytes())
    assert reader.read_bool() is True
    assert reader.read_byte() == -5
    assert reader.read_ubyte() == 250
    assert reader.read_short() == -1234
    assert reader.read_ushort() == 50000
    assert reader.read_int() == -987654
    assert reader.read_long() == 1234567890123
    assert pytest.approx(reader.read_float(), rel=1e-5) == 3.14159
    assert pytest.approx(reader.read_double(), rel=1e-9) == 2.718281828
    assert reader.read_string() == "Hello Minecraft"
    assert reader.read_uuid() == test_uuid
    assert reader.read_position() == test_pos
    assert reader.remaining == 0


def test_encryption_cfb8():
    secret = os.urandom(16)
    cipher = EncryptionCipher(secret)
    decipher = EncryptionCipher(secret)

    plaintext = b"Minecraft network protocol encryption test data 12345!"
    encrypted = cipher.encrypt(plaintext)
    assert encrypted != plaintext

    decrypted = decipher.decrypt(encrypted)
    assert decrypted == plaintext


@pytest.mark.asyncio
async def test_packet_framing_uncompressed():
    framer = PacketFramer(compression_threshold=-1)
    payload = b"\x01\x02\x03\x04\x05"
    packet_id = 0x0A

    framed_data = framer.frame_packet(packet_id, payload)

    # Use StreamReader to test decoding
    stream_reader = asyncio.StreamReader()
    stream_reader.feed_data(framed_data)
    stream_reader.feed_eof()

    read_id, read_payload = await framer.read_packet_frame(stream_reader)
    assert read_id == packet_id
    assert read_payload == payload


@pytest.mark.asyncio
async def test_packet_framing_compressed():
    framer = PacketFramer(compression_threshold=16)
    # 1. Payload smaller than threshold
    small_payload = b"small"
    framed_small = framer.frame_packet(0x01, small_payload)

    stream1 = asyncio.StreamReader()
    stream1.feed_data(framed_small)
    stream1.feed_eof()
    r_id, r_payload = await framer.read_packet_frame(stream1)
    assert r_id == 0x01
    assert r_payload == small_payload

    # 2. Large payload exceeding threshold (should be compressed)
    large_payload = b"large repetitive test data string " * 50
    framed_large = framer.frame_packet(0x02, large_payload)

    stream2 = asyncio.StreamReader()
    stream2.feed_data(framed_large)
    stream2.feed_eof()
    r_id2, r_payload2 = await framer.read_packet_frame(stream2)
    assert r_id2 == 0x02
    assert r_payload2 == large_payload


def test_protocol_registry_packets():
    registry = ProtocolRegistry.for_version("1.20.1")

    # Handshake
    handshake = HandshakePacket(
        protocol_version=DEFAULT_PROTOCOL_VERSION,
        server_address="localhost",
        server_port=25565,
        next_state=2,
    )
    encoded = handshake.encode()
    decoded = registry.decode_packet(
        ProtocolState.HANDSHAKING, is_serverbound=True, packet_id=0x00, payload=encoded
    )
    assert isinstance(decoded, HandshakePacket)
    assert decoded.server_address == "localhost"
    assert decoded.server_port == 25565
    assert decoded.next_state == 2

    # Login Start
    login_start = LoginStartPacket(name_str="TestBot")
    encoded_login = login_start.encode()
    decoded_login = registry.decode_packet(
        ProtocolState.LOGIN, is_serverbound=True, packet_id=0x00, payload=encoded_login
    )
    assert isinstance(decoded_login, LoginStartPacket)
    assert decoded_login.name_str == "TestBot"

    # Synchronize Position
    sync_pos = SynchronizePositionPacket(
        x=10.5, y=64.0, z=-20.5, yaw=90.0, pitch=0.0, flags=0, teleport_id=42
    )
    encoded_sync = sync_pos.encode()
    decoded_sync = registry.decode_packet(
        ProtocolState.PLAY, is_serverbound=False, packet_id=0x3E, payload=encoded_sync
    )
    assert isinstance(decoded_sync, SynchronizePositionPacket)
    assert decoded_sync.x == 10.5
    assert decoded_sync.teleport_id == 42
