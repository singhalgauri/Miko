# Owner: Person 2
# Purpose: Background worker service manager for Miko always-on operation
# TODO(person2): Implement cross-platform daemon process lifecycle and watchdog

import asyncio

from backend.app.core.logging import logger


class BackgroundServiceManager:
    """Coordinates background workers, periodic jobs, and system event watchers."""

    def __init__(self):
        self._running = False
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        """Starts background worker loop."""
        logger.info("Starting Miko background service manager")
        self._running = True
        self._task = asyncio.create_task(self._run_loop())

    async def stop(self) -> None:
        """Stops background worker loop."""
        logger.info("Stopping Miko background service manager")
        self._running = False
        if self._task:
            self._task.cancel()

    async def _run_loop(self) -> None:
        while self._running:
            try:
                # Periodic heartbeat check
                logger.debug("Background worker heartbeat tick")
                await asyncio.sleep(60)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in background worker tick: %s", e)
                await asyncio.sleep(5)


background_manager = BackgroundServiceManager()
