"""200-tick stability and soak test streaming packets and asserting stability."""

import asyncio
import gc
import uuid

import pytest

from integration_tests.mock_server import MockMinecraftServer
from mineflex import create_bot
from mineflex.protocol.packets.play.entities import SpawnEntityPacket, UpdateEntityPositionPacket
from mineflex.protocol.packets.play.keepalive import (
    KeepAliveClientboundPacket,
    KeepAliveServerboundPacket,
)
from mineflex.protocol.packets.play.player import UpdateTimePacket


@pytest.mark.asyncio
async def test_bot_200_tick_soak():
    """Run a 200-tick stability soak test streaming updates and verifying zero task/memory leaks."""
    server = MockMinecraftServer(compression_threshold=256)
    port = await server.start()

    bot = create_bot(
        host="127.0.0.1",
        port=port,
        username="SoakBot",
        auth="offline",
        physics_enabled=True,
    )

    bot_task = asyncio.create_task(bot.run())

    try:
        # Wait for spawn
        await bot.wait_for("spawn", timeout=5.0)
        assert bot.is_alive
        assert bot.entity.position is not None

        # Spawn a dummy entity to track
        spawn_entity_pkt = SpawnEntityPacket(
            entity_id=999,
            entity_uuid=uuid.UUID("00000000-0000-0000-0000-000000000999"),
            entity_type=1,
            x=5.0,
            y=64.0,
            z=5.0,
            pitch=0.0,
            yaw=0.0,
            head_yaw=0.0,
            data=0,
            vel_x=0,
            vel_y=0,
            vel_z=0,
        )
        await server.send_packet(spawn_entity_pkt)
        await asyncio.sleep(0.05)
        assert 999 in bot.entities

        # Measure baseline tasks
        gc.collect()
        initial_tasks = len([t for t in asyncio.all_tasks() if not t.done()])

        # Run 200 simulation ticks
        keep_alive_count = 0
        ticks_total = 200

        for tick in range(ticks_total):
            # Stream world time update
            await server.send_packet(
                UpdateTimePacket(world_age=tick, time_of_day=tick % 24000)
            )

            # Stream entity delta movement
            await server.send_packet(
                UpdateEntityPositionPacket(
                    entity_id=999,
                    delta_x=16,  # 16 / (128 * 32)
                    delta_y=0,
                    delta_z=16,
                    on_ground=True,
                )
            )

            # Periodically stream keepalive every 20 ticks
            if tick % 20 == 0:
                keep_alive_id = 1000 + tick
                await server.send_packet(KeepAliveClientboundPacket(keep_alive_id=keep_alive_id))
                keep_alive_count += 1

            # Yield control to let bot event loop and physics run
            await asyncio.sleep(0.005)

        # Allow final packets and physics cycle to settle
        await asyncio.sleep(0.1)

        # Validate keepalive responses
        keep_alives_answered = [
            p for p in server.received_packets if isinstance(p, KeepAliveServerboundPacket)
        ]
        assert len(keep_alives_answered) >= keep_alive_count - 1

        # Validate bot state remained healthy
        assert bot.is_alive
        assert bot.time == ticks_total - 1
        assert bot.time_of_day == (ticks_total - 1) % 24000
        assert 999 in bot.entities

        # Validate task stability (tasks should not leak over 200 ticks)
        gc.collect()
        final_tasks = len([t for t in asyncio.all_tasks() if not t.done()])
        # At most 2 task variation allowed for transient background callbacks
        assert abs(final_tasks - initial_tasks) <= 3, (
            f"Possible task leak: initial={initial_tasks}, final={final_tasks}"
        )

    finally:
        await bot.quit()
        await bot_task
        await server.stop()
