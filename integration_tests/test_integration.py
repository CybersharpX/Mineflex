"""End-to-end integration tests using in-process Mock Minecraft Server."""

import asyncio

import pytest

from integration_tests.mock_server import MockMinecraftServer
from mineflex import create_bot
from mineflex.constants import DiggingStatus, InteractType
from mineflex.protocol.packets.play.chat import ChatMessagePacket
from mineflex.protocol.packets.play.entities import InteractPacket
from mineflex.protocol.packets.play.player import PlayerActionPacket
from mineflex.types import Vec3


@pytest.mark.asyncio
async def test_bot_connect_and_spawn():
    server = MockMinecraftServer(compression_threshold=-1)
    port = await server.start()

    bot = create_bot(
        host="127.0.0.1",
        port=port,
        username="TesterBot",
        auth="offline",
        physics_enabled=False,
    )

    bot_task = asyncio.create_task(bot.run())

    try:
        await bot.wait_for("spawn", timeout=5.0)
        assert bot.username == "TesterBot"
        assert bot.position == Vec3(0.5, 64.0, 0.5)
        assert bot.health == 20.0
    finally:
        await bot.quit()
        await bot_task
        await server.stop()


@pytest.mark.asyncio
async def test_bot_chat_echo():
    server = MockMinecraftServer()
    port = await server.start()

    bot = create_bot(
        host="127.0.0.1",
        port=port,
        username="EchoBot",
        auth="offline",
        physics_enabled=False,
    )

    @bot.on("chat")
    async def on_chat(username, message, *args):
        if username != bot.username:
            await bot.chat(f"Echo: {message}")

    bot_task = asyncio.create_task(bot.run())

    try:
        await bot.wait_for("spawn", timeout=5.0)

        # Server sends chat from Steve
        await server.broadcast_chat("<Steve> Hello Mineflex")

        # Server should receive bot's echo
        echo_pkt = await server.wait_for_packet(ChatMessagePacket, timeout=3.0)
        assert isinstance(echo_pkt, ChatMessagePacket)
        assert echo_pkt.message == "Echo: Hello Mineflex"
    finally:
        await bot.quit()
        await bot_task
        await server.stop()


@pytest.mark.asyncio
async def test_bot_dig_block():
    server = MockMinecraftServer()
    port = await server.start()

    bot = create_bot(
        host="127.0.0.1",
        port=port,
        username="MinerBot",
        auth="offline",
        physics_enabled=False,
    )

    bot_task = asyncio.create_task(bot.run())

    try:
        await bot.wait_for("spawn", timeout=5.0)

        # Place a stone block within reach at (0, 63, 0)
        bot.world.set_block_state(Vec3(0, 63, 0), 1)  # stone
        target_block = bot.block_at(Vec3(0, 63, 0))

        # Dig the stone block
        await bot.dig(target_block, force_look=False)

        # Allow small I/O buffer propagation
        await asyncio.sleep(0.1)

        # Server should receive start and finished digging packets
        dig_packets = [p for p in server.received_packets if isinstance(p, PlayerActionPacket)]
        statuses = [p.status for p in dig_packets]
        assert DiggingStatus.STARTED_DIGGING in statuses
        assert DiggingStatus.FINISHED_DIGGING in statuses
    finally:
        await bot.quit()
        await bot_task
        await server.stop()


@pytest.mark.asyncio
async def test_bot_attack_entity():
    server = MockMinecraftServer()
    port = await server.start()

    bot = create_bot(
        host="127.0.0.1",
        port=port,
        username="CombatBot",
        auth="offline",
        physics_enabled=False,
    )

    bot_task = asyncio.create_task(bot.run())

    try:
        await bot.wait_for("spawn", timeout=5.0)

        # Server spawns zombie near bot at (1.0, 64.0, 1.0)
        await server.spawn_mob(entity_id=100, entity_type=125, x=1.0, y=64.0, z=1.0)
        await asyncio.sleep(0.1)

        target_mob = bot.nearest_entity(lambda e: e.name == "zombie")
        assert target_mob is not None
        assert target_mob.id == 100

        await bot.attack(target_mob)

        # Server should receive InteractPacket (ATTACK)
        attack_pkt = await server.wait_for_packet(InteractPacket, timeout=3.0)
        assert isinstance(attack_pkt, InteractPacket)
        assert attack_pkt.entity_id == 100
        assert attack_pkt.interact_type == InteractType.ATTACK
    finally:
        await bot.quit()
        await bot_task
        await server.stop()


@pytest.mark.asyncio
async def test_compression_negotiation():
    # Start server with compression threshold 128
    server = MockMinecraftServer(compression_threshold=128)
    port = await server.start()

    bot = create_bot(
        host="127.0.0.1",
        port=port,
        username="CompressedBot",
        auth="offline",
        physics_enabled=False,
    )

    bot_task = asyncio.create_task(bot.run())

    try:
        await bot.wait_for("spawn", timeout=5.0)
        # Verify bot framer updated compression threshold
        assert bot.client.framer.compression_threshold == 128
        assert bot.position == Vec3(0.5, 64.0, 0.5)
    finally:
        await bot.quit()
        await bot_task
        await server.stop()
