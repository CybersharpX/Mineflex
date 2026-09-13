"""The central Bot client implementation for Mineflex."""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

from mineflex.auth.base import Session
from mineflex.auth.offline import OfflineAuthProvider
from mineflex.client.connection import ClientConnection
from mineflex.constants import (
    DEFAULT_MINECRAFT_VERSION,
    DEFAULT_PROTOCOL_VERSION,
    ProtocolState,
)
from mineflex.data.provider import Registry
from mineflex.entity.entity import Entity
from mineflex.entity.player import Player
from mineflex.errors import InvalidStateError, ProtocolError
from mineflex.events.emitter import AsyncEventEmitter
from mineflex.logging import get_logger
from mineflex.plugins.base import PluginManager, PluginType
from mineflex.plugins.internal import STANDARD_INTERNAL_PLUGINS
from mineflex.protocol.packets.handshake import HandshakePacket
from mineflex.protocol.packets.login import (
    DisconnectLoginPacket,
    LoginStartPacket,
    LoginSuccessPacket,
)
from mineflex.protocol.packets.play.player import ClientInformationPacket
from mineflex.types import Vec3

logger = get_logger("mineflex.bot")


class Bot(AsyncEventEmitter):
    """The central Minecraft bot client instance."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 25565,
        username: str = "Bot",
        auth: str = "offline",
        version: str = DEFAULT_MINECRAFT_VERSION,
        password: Optional[str] = None,
        keep_alive: bool = True,
        timeout: float = 30.0,
        physics_enabled: bool = True,
        respawn: bool = True,
        plugins: Optional[List[PluginType]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__()
        self.host = host
        self.port = port
        self.username = username
        self.auth_mode = auth
        self.version_str = version
        self.password = password
        self.keep_alive_enabled = keep_alive
        self.timeout = timeout
        self.physics_enabled = physics_enabled
        self.respawn_enabled = respawn
        self.extra_options = kwargs

        # Registries and data
        self.registry = Registry(self.version_str)
        self.protocol_version = DEFAULT_PROTOCOL_VERSION

        # Client Connection
        self.client = ClientConnection(
            host=self.host,
            port=self.port,
            protocol_version=self.protocol_version,
            timeout=self.timeout,
        )

        # Entity representation of the bot itself
        self.session: Optional[Session] = None
        self.entity = Entity(
            id=0,
            uuid=OfflineAuthProvider().authenticate(username).__await__().__next__().player_uuid
            if False
            else None,  # assigned on login
            type=116,  # player
            name=self.username,
            position=Vec3(0, 64, 0),
        )

        # Plugins
        self.plugin_manager = PluginManager(self)
        self._initial_custom_plugins = list(plugins or [])

        # Internal state
        self._running = False
        self._stop_event = asyncio.Event()

    @property
    def entities(self) -> Dict[int, Entity]:
        return (
            getattr(self, "entity_tracker", None).entities
            if hasattr(self, "entity_tracker")
            else {}
        )

    @property
    def players(self) -> Dict[str, Player]:
        return (
            getattr(self, "entity_tracker", None).players if hasattr(self, "entity_tracker") else {}
        )

    @property
    def position(self) -> Vec3:
        return self.entity.position

    def load_plugin(self, plugin: PluginType) -> None:
        self.plugin_manager.load_plugin(plugin)

    def load_plugins(self, plugins: List[PluginType]) -> None:
        self.plugin_manager.load_plugins(plugins)

    def has_plugin(self, plugin: PluginType) -> bool:
        return self.plugin_manager.has_plugin(plugin)

    async def run(self) -> None:
        """Start the bot, connect to the Minecraft server, and run the event loop."""
        if self._running:
            raise InvalidStateError("Bot is already running")
        self._running = True
        self._stop_event.clear()

        try:
            # 1. Authenticate (offline mode)
            auth_provider = OfflineAuthProvider()
            self.session = await auth_provider.authenticate(self.username)
            self.entity.uuid = self.session.player_uuid

            # 2. Inject internal core plugins
            for plugin_func in STANDARD_INTERNAL_PLUGINS:
                plugin_func(self)

            # Load user-provided custom plugins
            for p in self._initial_custom_plugins:
                self.load_plugin(p)

            # 3. Connect to TCP server
            await self.client.connect()
            await self.emit("connect")

            # 4. Perform Handshake & Login
            await self._perform_handshake_and_login()

            # 5. Wait until bot disconnects
            await self._stop_event.wait()

        except asyncio.CancelledError:
            pass
        except Exception as exc:
            logger.error("Bot run error: %s", exc, exc_info=True)
            await self.emit("error", exc)
        finally:
            await self.quit("Session ended")

    async def _perform_handshake_and_login(self) -> None:
        """Execute handshake and login protocol sequence."""
        # 1. Send Handshake
        handshake = HandshakePacket(
            protocol_version=self.protocol_version,
            server_address=self.host,
            server_port=self.port,
            next_state=2,  # Login
        )
        await self.client.send_packet(handshake)
        self.client.set_state(ProtocolState.LOGIN)

        # 2. Send Login Start
        login_start = LoginStartPacket(
            name_str=self.username,
            player_uuid=self.session.player_uuid if self.session else None,
        )
        await self.client.send_packet(login_start)

        login_future: asyncio.Future[None] = asyncio.get_running_loop().create_future()

        def on_login_success(packet: LoginSuccessPacket) -> None:
            self.entity.uuid = packet.player_uuid
            self.username = packet.username
            self.client.set_state(ProtocolState.PLAY)
            if not login_future.done():
                login_future.set_result(None)

        def on_disconnect_login(packet: DisconnectLoginPacket) -> None:
            err = ProtocolError(f"Kicked during login: {packet.reason}")
            if not login_future.done():
                login_future.set_exception(err)

        self.client.register_handler(LoginSuccessPacket, on_login_success)
        self.client.register_handler(DisconnectLoginPacket, on_disconnect_login)

        # Wait for login success
        await asyncio.wait_for(login_future, timeout=self.timeout)

        # Send Client Information packet
        await self.client.send_packet(ClientInformationPacket())
        await self.emit("login")

    async def quit(self, reason: str = "Quitting") -> None:
        """Gracefully disconnect and shut down bot tasks."""
        if not self._running:
            return
        self._running = False
        self._stop_event.set()

        # Stop physics simulation task if active
        if hasattr(self, "_physics_task") and self._physics_task and not self._physics_task.done():
            self._physics_task.cancel()

        if self.client.is_connected:
            await self.client.disconnect(reason=reason)

        await self.emit("end", reason)

    end = quit


def create_bot(
    host: str = "localhost",
    port: int = 25565,
    username: str = "Bot",
    auth: str = "offline",
    version: str = DEFAULT_MINECRAFT_VERSION,
    password: Optional[str] = None,
    keep_alive: bool = True,
    timeout: float = 30.0,
    physics_enabled: bool = True,
    respawn: bool = True,
    plugins: Optional[List[PluginType]] = None,
    **kwargs: Any,
) -> Bot:
    """Convenience factory creating and configuring a Bot instance."""
    return Bot(
        host=host,
        port=port,
        username=username,
        auth=auth,
        version=version,
        password=password,
        keep_alive=keep_alive,
        timeout=timeout,
        physics_enabled=physics_enabled,
        respawn=respawn,
        plugins=plugins,
        **kwargs,
    )
