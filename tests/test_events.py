"""Unit tests for AsyncEventEmitter."""

import asyncio

import pytest

from mineflex.events.emitter import AsyncEventEmitter


@pytest.mark.asyncio
async def test_event_emitter_sync_and_async_listeners():
    emitter = AsyncEventEmitter()
    results = []

    def sync_listener(val):
        results.append(f"sync:{val}")

    async def async_listener(val):
        await asyncio.sleep(0.01)
        results.append(f"async:{val}")

    emitter.on("test", sync_listener)
    emitter.on("test", async_listener)

    await emitter.emit("test", 42)
    assert "sync:42" in results
    assert "async:42" in results


@pytest.mark.asyncio
async def test_event_emitter_once():
    emitter = AsyncEventEmitter()
    count = 0

    @emitter.once("ping")
    def on_ping():
        nonlocal count
        count += 1

    await emitter.emit("ping")
    await emitter.emit("ping")
    assert count == 1


@pytest.mark.asyncio
async def test_event_emitter_off():
    emitter = AsyncEventEmitter()
    calls = []

    def handler():
        calls.append(1)

    emitter.on("event", handler)
    await emitter.emit("event")
    assert len(calls) == 1

    emitter.off("event", handler)
    await emitter.emit("event")
    assert len(calls) == 1


@pytest.mark.asyncio
async def test_event_emitter_error_isolation():
    emitter = AsyncEventEmitter()
    executed = []

    def broken_handler():
        raise RuntimeError("Something broke!")

    def working_handler():
        executed.append(True)

    emitter.on("test", broken_handler)
    emitter.on("test", working_handler)

    # Should not raise exception
    await emitter.emit("test")
    assert executed == [True]


@pytest.mark.asyncio
async def test_event_emitter_wait_for():
    emitter = AsyncEventEmitter()

    async def trigger():
        await asyncio.sleep(0.05)
        await emitter.emit("custom", "hello", 123)

    task = asyncio.create_task(trigger())
    val = await emitter.wait_for("custom", timeout=1.0)
    assert val == ("hello", 123)
    await task
