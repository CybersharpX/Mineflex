"""In-process mock Minecraft server for end-to-end integration testing."""

from __future__ import annotations

import asyncio
import json
import uuid
from typing import List, Optional

from mineflex.constants import DEFAULT_PROTOCOL_VERSION, ProtocolState
from mineflex.errors import ConnectionError as MineflexConnectionError
from mineflex.logging import get_logger
from mineflex.protocol.buffer import PacketWriter
from mineflex.protocol.framing import PacketFramer
from mineflex.protocol.packets.handshake import HandshakePacket
from mineflex.protocol.packets.login import (
    LoginStartPacket,
    LoginSuccessPacket,
    SetCompressionPacket,
)
from mineflex.protocol.packets.play.chat import SystemChatPacket
from mineflex.protocol.packets.play.entities import SpawnEntityPacket
from mineflex.protocol.packets.play.player import (
    LoginPlayPacket,
    SetHealthPacket,
    SynchronizePositionPacket,
)
from mineflex.protocol.packets.play.world import ChunkDataPacket
from mineflex.protocol.registry import Packet, ProtocolRegistry

logger = get_logger("mineflex.mock_server")


class MockMinecraftServer:
    """A lightweight in-process Minecraft Java Edition server for automated tests."""

    def __init__(
        self,
        host: str = "127.0.0.1",
        compression_threshold: int = -1,
        protocol_version: int = DEFAULT_PROTOCOL_VERSION,
    ) -> None:
        self.host = host
        self.port: int = 0
        self.target_compression_threshold = compression_threshold
        self.protocol_version = protocol_version

        self.registry = ProtocolRegistry.for_version(protocol_version)
        # Always start unframed / uncompressed during Handshake & LoginStart
        self.framer = PacketFramer(compression_threshold=-1)

        self._server: Optional[asyncio.Server] = None
        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None
        self._serve_task: Optional[asyncio.Task] = None

        self.state = ProtocolState.HANDSHAKING
        self.received_packets: List[Packet] = []
        self.packet_received_event = asyncio.Event()

    async def start(self) -> int:
        """Start listening on an ephemeral port and return the port number."""
        self._server = await asyncio.start_server(self._handle_client, self.host, 0)
        sock = self._server.sockets[0]
        self.port = sock.getsockname()[1]
        logger.info("Mock Minecraft server listening on %s:%d", self.host, self.port)
        return self.port

    async def stop(self) -> None:
        """Stop mock server and disconnect clients."""
        if self._writer:
            try:
                self._writer.close()
                await self._writer.wait_closed()
            except Exception:
                pass

        if self._server:
            self._server.close()
            await self._server.wait_closed()

        if self._serve_task and not self._serve_task.done():
            self._serve_task.cancel()
            try:
                await self._serve_task
            except (asyncio.CancelledError, Exception):
                pass

    async def _handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        self._reader = reader
        self._writer = writer
        self._serve_task = asyncio.create_task(self._read_loop())

    async def _read_loop(self) -> None:
        try:
            while self._reader and not self._reader.at_eof():
                packet_id, payload = await self.framer.read_packet_frame(self._reader)
                packet = self.registry.decode_packet(
                    state=self.state,
                    is_serverbound=True,
                    packet_id=packet_id,
                    payload=payload,
                )
                if packet:
                    self.received_packets.append(packet)
                    self.packet_received_event.set()
                    await self._handle_packet(packet)
        except (
            asyncio.IncompleteReadError,
            asyncio.CancelledError,
            ConnectionResetError,
            MineflexConnectionError,
        ):
            pass
        except Exception as exc:
            logger.error("Mock server client error: %s", exc)

    async def _handle_packet(self, packet: Packet) -> None:
        if isinstance(packet, HandshakePacket):
            if packet.next_state == 2:
                self.state = ProtocolState.LOGIN

        elif isinstance(packet, LoginStartPacket):
            # If server enables compression, send SetCompressionPacket uncompressed,
            # then enable compression on the framer
            if self.target_compression_threshold >= 0:
                await self.send_packet(
                    SetCompressionPacket(threshold=self.target_compression_threshold)
                )
                self.framer.set_compression_threshold(self.target_compression_threshold)

            # Send Login Success
            player_uuid = packet.player_uuid or uuid.uuid4()
            await self.send_packet(
                LoginSuccessPacket(player_uuid=player_uuid, username=packet.name_str)
            )
            self.state = ProtocolState.PLAY

            # Send initial play packets: LoginPlay, SynchronizePosition, SetHealth, Chunk
            await self.send_packet(LoginPlayPacket(entity_id=1, is_hardcore=False, gamemode=0))
            await self.send_packet(SetHealthPacket(health=20.0, food=20, food_saturation=5.0))

            # Send standard test chunk with ground blocks at Y=60-63
            await self._send_test_chunk()

            # Synchronize position
            await self.send_packet(
                SynchronizePositionPacket(
                    x=0.5,
                    y=64.0,
                    z=0.5,
                    yaw=0.0,
                    pitch=0.0,
                    flags=0,
                    teleport_id=1,
                )
            )

    async def _send_test_chunk(self) -> None:
        """Construct and send a test chunk containing flat stone floor."""
        writer = PacketWriter()
        # 24 chunk sections
        for sec_y in range(24):
            writer.write_short(0)
            writer.write_ubyte(0)
            state_id = 1 if sec_y == 7 else 0
            writer.write_varint(state_id)
            writer.write_varint(0)
            writer.write_ubyte(0)
            writer.write_varint(1)
            writer.write_varint(0)

        chunk_pkt = ChunkDataPacket(
            chunk_x=0,
            chunk_z=0,
            heightmaps=None,
            data=writer.get_bytes(),
            block_entities=[],
        )
        await self.send_packet(chunk_pkt)

    async def send_packet(self, packet: Packet) -> None:
        """Send framed packet from server to connected bot."""
        if not self._writer:
            return
        payload = packet.encode()
        framed = self.framer.frame_packet(packet.packet_id, payload)
        self._writer.write(framed)
        await self._writer.drain()

    async def broadcast_chat(self, message: str) -> None:
        """Send a chat message to the connected client."""
        payload_json = json.dumps({"text": message})
        await self.send_packet(SystemChatPacket(content=payload_json, overlay=False))

    async def spawn_mob(
        self, entity_id: int, entity_type: int, x: float, y: float, z: float
    ) -> None:
        """Spawn an entity near the bot."""
        pkt = SpawnEntityPacket(
            entity_id=entity_id,
            entity_uuid=uuid.uuid4(),
            entity_type=entity_type,
            x=x,
            y=y,
            z=z,
            pitch=0.0,
            yaw=0.0,
            head_yaw=0.0,
            data=0,
        )
        await self.send_packet(pkt)

    async def wait_for_packet(self, packet_type: type[Packet], timeout: float = 3.0) -> Packet:
        """Wait until a specific packet type is received from the bot."""
        loop = asyncio.get_running_loop()
        end_time = loop.time() + timeout
        while loop.time() < end_time:
            for p in self.received_packets:
                if isinstance(p, packet_type):
                    return p
            self.packet_received_event.clear()
            try:
                rem = end_time - loop.time()
                if rem <= 0:
                    break
                await asyncio.wait_for(self.packet_received_event.wait(), timeout=rem)
            except asyncio.TimeoutError:
                break

        for p in self.received_packets:
            if isinstance(p, packet_type):
                return p
        raise TimeoutError(f"Timed out waiting for packet {packet_type.__name__}")
