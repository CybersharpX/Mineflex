"""Asynchronous TCP client connection managing framing, state, and packet dispatch."""

from __future__ import annotations

import asyncio
from typing import Any, Callable, Coroutine, Dict, List, Optional, Type, Union

from mineflex.constants import DEFAULT_PROTOCOL_VERSION, ProtocolState
from mineflex.errors import ConnectionError
from mineflex.logging import get_logger
from mineflex.protocol.encryption import EncryptionCipher
from mineflex.protocol.framing import PacketFramer
from mineflex.protocol.packets.login import SetCompressionPacket
from mineflex.protocol.packets.play.keepalive import (
    KeepAliveClientboundPacket,
    KeepAliveServerboundPacket,
)
from mineflex.protocol.registry import Packet, ProtocolRegistry

logger = get_logger("mineflex.client")

PacketHandler = Union[Callable[[Any], Any], Callable[[Any], Coroutine[Any, Any, Any]]]


class ClientConnection:
    """Manages the low-level asynchronous network connection to a Minecraft server."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 25565,
        protocol_version: int = DEFAULT_PROTOCOL_VERSION,
        timeout: float = 30.0,
    ) -> None:
        self.host = host
        self.port = port
        self.protocol_version = protocol_version
        self.timeout = timeout

        self.state: ProtocolState = ProtocolState.HANDSHAKING
        self.registry: ProtocolRegistry = ProtocolRegistry.for_version(protocol_version)
        self.framer: PacketFramer = PacketFramer(compression_threshold=-1)
        self.cipher: Optional[EncryptionCipher] = None

        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self._receive_task: Optional[asyncio.Task] = None
        self._handlers: Dict[Any, List[PacketHandler]] = {}
        self._is_connected = False
        self._closed = False

    @property
    def is_connected(self) -> bool:
        return self._is_connected and not self._closed

    def register_handler(
        self, packet_type: Union[Type[Packet], int, str], handler: PacketHandler
    ) -> None:
        """Register a callback for incoming packets."""
        if packet_type not in self._handlers:
            self._handlers[packet_type] = []
        if handler not in self._handlers[packet_type]:
            self._handlers[packet_type].append(handler)

    def unregister_handler(
        self, packet_type: Union[Type[Packet], int, str], handler: PacketHandler
    ) -> None:
        if packet_type in self._handlers and handler in self._handlers[packet_type]:
            self._handlers[packet_type].remove(handler)

    async def connect(self) -> None:
        """Open TCP connection to Minecraft server."""
        try:
            self.reader, self.writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=self.timeout,
            )
            self._is_connected = True
            self._closed = False
            self._receive_task = asyncio.create_task(self._receive_loop())
            logger.info("Connected to %s:%d", self.host, self.port)
        except Exception as exc:
            self._is_connected = False
            raise ConnectionError(f"Failed to connect to {self.host}:{self.port}: {exc}") from exc

    def set_state(self, state: ProtocolState) -> None:
        """Transition connection to a new protocol state."""
        logger.debug("State transition: %s -> %s", self.state.name, state.name)
        self.state = state

    def set_compression(self, threshold: int) -> None:
        """Enable packet compression with given threshold."""
        logger.debug("Setting compression threshold: %d", threshold)
        self.framer.set_compression_threshold(threshold)

    def enable_encryption(self, shared_secret: bytes) -> None:
        """Enable AES-128 CFB8 stream encryption."""
        logger.debug("Enabling AES-128 CFB8 network encryption")
        self.cipher = EncryptionCipher(shared_secret)

    async def send_packet(self, packet: Packet) -> None:
        """Encode, frame, and send a typed packet."""
        if not self.is_connected or self.writer is None:
            raise ConnectionError("Cannot send packet: client is disconnected")

        payload = packet.encode()
        framed = self.framer.frame_packet(packet.packet_id, payload)

        if self.cipher:
            framed = self.cipher.encrypt(framed)

        self.writer.write(framed)
        await self.writer.drain()
        logger.debug(
            "Sent packet %s (0x%02X, %d bytes)", packet.name, packet.packet_id, len(framed)
        )

    async def disconnect(self, reason: str = "Client disconnected") -> None:
        """Disconnect and close network resources cleanly."""
        if self._closed:
            return
        self._closed = True
        self._is_connected = False
        logger.info("Disconnecting: %s", reason)

        if self._receive_task and not self._receive_task.done():
            self._receive_task.cancel()
            try:
                await self._receive_task
            except (asyncio.CancelledError, Exception):
                pass

        if self.writer:
            try:
                self.writer.close()
                await self.writer.wait_closed()
            except Exception:
                pass

    async def _receive_loop(self) -> None:
        """Internal background loop reading and dispatching packets."""
        try:
            while self.is_connected and self.reader:
                packet_id, payload = await self.framer.read_packet_frame(self.reader)

                packet = self.registry.decode_packet(
                    state=self.state,
                    is_serverbound=False,
                    packet_id=packet_id,
                    payload=payload,
                )

                # Automatic internal handling
                if isinstance(packet, SetCompressionPacket):
                    self.set_compression(packet.threshold)
                elif isinstance(packet, KeepAliveClientboundPacket):
                    # Automatic Keep-Alive reply
                    await self.send_packet(
                        KeepAliveServerboundPacket(keep_alive_id=packet.keep_alive_id)
                    )

                # Dispatch to registered handlers
                await self._dispatch_packet(packet_id, payload, packet)

        except asyncio.CancelledError:
            pass
        except Exception as exc:
            if not self._closed:
                logger.error("Connection receive error: %s", exc)
                self._is_connected = False
                await self.disconnect(reason=str(exc))

    async def _dispatch_packet(
        self, packet_id: int, payload: bytes, packet: Optional[Packet]
    ) -> None:
        handlers: List[PacketHandler] = []

        if packet is not None:
            handlers.extend(self._handlers.get(type(packet), []))
            handlers.extend(self._handlers.get(packet.name, []))
        handlers.extend(self._handlers.get(packet_id, []))
        handlers.extend(self._handlers.get("*", []))

        arg = packet if packet is not None else (packet_id, payload)
        for h in handlers:
            try:
                res = h(arg)
                if asyncio.iscoroutine(res):
                    await res
            except Exception as exc:
                logger.error("Error in packet handler: %s", exc, exc_info=True)
