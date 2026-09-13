"""Asynchronous event emitter with robust error isolation and introspection."""

from __future__ import annotations

import asyncio
import inspect
from typing import Any, Callable, Coroutine, Optional, Union

from mineflex.logging import get_logger

logger = get_logger("mineflex.events")

EventListener = Union[Callable[..., Any], Callable[..., Coroutine[Any, Any, Any]]]


class AsyncEventEmitter:
    """Event emitter supporting sync and async listeners with safe exception isolation."""

    def __init__(self) -> None:
        self._listeners: dict[str, list[EventListener]] = {}
        self._once_listeners: dict[str, set[EventListener]] = {}

    def on(
        self, event: str, listener: Optional[EventListener] = None
    ) -> Union[EventListener, Callable[[EventListener], EventListener]]:
        """Register an event listener. Can be used as a function or as a decorator."""
        if listener is None:

            def decorator(fn: EventListener) -> EventListener:
                self._add_listener(event, fn, once=False)
                return fn

            return decorator

        self._add_listener(event, listener, once=False)
        return listener

    def once(
        self, event: str, listener: Optional[EventListener] = None
    ) -> Union[EventListener, Callable[[EventListener], EventListener]]:
        """Register a one-time event listener. Can be used as a function or as a decorator."""
        if listener is None:

            def decorator(fn: EventListener) -> EventListener:
                self._add_listener(event, fn, once=True)
                return fn

            return decorator

        self._add_listener(event, listener, once=True)
        return listener

    def _add_listener(self, event: str, listener: EventListener, once: bool) -> None:
        if event not in self._listeners:
            self._listeners[event] = []
            self._once_listeners[event] = set()

        if listener not in self._listeners[event]:
            self._listeners[event].append(listener)
            if once:
                self._once_listeners[event].add(listener)

    def off(self, event: str, listener: EventListener) -> None:
        """Remove an event listener."""
        if event in self._listeners:
            if listener in self._listeners[event]:
                self._listeners[event].remove(listener)
            if event in self._once_listeners and listener in self._once_listeners[event]:
                self._once_listeners[event].remove(listener)

    remove_listener = off

    def remove_all_listeners(self, event: Optional[str] = None) -> None:
        """Remove all listeners, optionally restricted to a specific event."""
        if event is not None:
            self._listeners.pop(event, None)
            self._once_listeners.pop(event, None)
        else:
            self._listeners.clear()
            self._once_listeners.clear()

    def listeners(self, event: str) -> list[EventListener]:
        """Return a copy of the list of listeners registered for an event."""
        return list(self._listeners.get(event, []))

    def listener_count(self, event: str) -> int:
        """Return the number of listeners registered for an event."""
        return len(self._listeners.get(event, []))

    async def emit(self, event: str, *args: Any, **kwargs: Any) -> None:
        """Dispatch an event to all registered listeners.

        Runs listeners safely, isolating exceptions so that one failing listener does
        not prevent others from running or crash the event loop.
        """
        registered = list(self._listeners.get(event, []))
        if not registered:
            return

        once_set = self._once_listeners.get(event, set())
        to_remove = [fn for fn in registered if fn in once_set]
        for fn in to_remove:
            self.off(event, fn)

        for fn in registered:
            try:
                if inspect.iscoroutinefunction(fn):
                    await fn(*args, **kwargs)
                else:
                    res = fn(*args, **kwargs)
                    if inspect.isawaitable(res):
                        await res
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                logger.error(
                    "Unhandled exception in listener %s for event '%s': %s",
                    getattr(fn, "__qualname__", repr(fn)),
                    event,
                    exc,
                    exc_info=True,
                )

    def emit_sync(self, event: str, *args: Any, **kwargs: Any) -> None:
        """Schedule event emission on the current running event loop without awaiting it."""
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.emit(event, *args, **kwargs))
        except RuntimeError:
            # If no running loop, call only sync listeners synchronously
            registered = list(self._listeners.get(event, []))
            for fn in registered:
                if not inspect.iscoroutinefunction(fn):
                    try:
                        fn(*args, **kwargs)
                    except Exception as exc:
                        logger.error("Exception in sync listener for '%s': %s", event, exc)

    async def wait_for(
        self,
        event: str,
        timeout: Optional[float] = None,
        check: Optional[Callable[..., bool]] = None,
    ) -> Any:
        """Wait until an event is emitted matching an optional check condition."""
        loop = asyncio.get_running_loop()
        future = loop.create_future()

        def handler(*args: Any) -> None:
            try:
                if check is None or check(*args):
                    self.off(event, handler)
                    if not future.done():
                        future.set_result(
                            args[0] if len(args) == 1 else args if len(args) > 1 else None
                        )
            except Exception as exc:
                self.off(event, handler)
                if not future.done():
                    future.set_exception(exc)

        self.on(event, handler)
        try:
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            self.off(event, handler)
            raise
