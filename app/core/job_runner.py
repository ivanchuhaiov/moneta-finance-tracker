from datetime import datetime, timezone
from typing import Any, Awaitable, Callable

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.core.enums import JobStatus
from app.models.scheduled_job_log import ScheduledJobLog


async def run_with_logging(job_name: str, job_func: Callable[[AsyncSession], Awaitable[Any]]) -> None:
    async with async_session_factory() as session:
        log_entry = ScheduledJobLog(job_name=job_name, status=JobStatus.RUNNING, started_at=datetime.now(timezone.utc))
        session.add(log_entry)
        await session.commit()
        await session.refresh(log_entry)

    async with async_session_factory() as session:
        try:
            result = await job_func(session)
            log_entry.status = JobStatus.SUCCESS
            if isinstance(result, list):
                log_entry.details = f"processed {len(result)} items"
            else:
                log_entry.details = str(result) if result else None
        except Exception as e:
            log_entry.status = JobStatus.FAILED
            log_entry.error_message = str(e)
        finally:
            log_entry.finished_at = datetime.now(timezone.utc)
            await session.merge(log_entry)
            await session.commit()