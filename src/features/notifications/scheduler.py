import asyncio
import logging
import os
from datetime import datetime
from datetime import timezone

from src.core.uow import UnitOfWork

logger = logging.getLogger("app.notifications.scheduler")


class NotificationScheduler:
    def __init__(self):
        self._stop_event = asyncio.Event()
        self._task: asyncio.Task | None = None
        self._interval_seconds = max(
            5,
            int(os.getenv("NOTIFICATION_DISPATCH_INTERVAL_SECONDS", "30")),
        )

    def start(self) -> None:
        if self._task is not None and not self._task.done():
            return
        self._stop_event.clear()
        self._task = asyncio.create_task(self._run_loop(), name="notification-dispatch-loop")

    async def stop(self) -> None:
        if self._task is None:
            return

        self._stop_event.set()
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass

        self._task = None

    async def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                with UnitOfWork() as uow:
                    created_count = uow.notifications.dispatch_due(datetime.now(timezone.utc))
                    if created_count > 0:
                        logger.info("dispatched scheduled notifications count=%s", created_count)
            except Exception:
                logger.exception("failed to dispatch due notifications")

            try:
                await asyncio.wait_for(self._stop_event.wait(), timeout=self._interval_seconds)
            except asyncio.TimeoutError:
                continue


scheduler = NotificationScheduler()


def is_scheduler_enabled() -> bool:
    return os.getenv("NOTIFICATION_SCHEDULER_ENABLED", "true").strip().lower() == "true"
