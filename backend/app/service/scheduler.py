# Owner: Person 2
# Purpose: Task scheduler for periodic triggers (inbox sync, daily briefing, catch-up)
# TODO(person2): Add cron-like expression support and persistent scheduling queues

from typing import Any, Callable

from backend.app.core.logging import logger


class TaskScheduler:
    """Manages scheduled background recurring jobs."""

    def __init__(self):
        self._jobs: dict[str, dict[str, Any]] = {}

    def schedule_recurring(self, name: str, interval_seconds: int, callback: Callable) -> None:
        """Registers a recurring task."""
        logger.info("Scheduling task '%s' every %d seconds", name, interval_seconds)
        self._jobs[name] = {
            "interval": interval_seconds,
            "callback": callback,
            "status": "scheduled",
        }

    def list_jobs(self) -> dict[str, dict[str, Any]]:
        """Returns registered jobs."""
        return self._jobs


scheduler = TaskScheduler()
