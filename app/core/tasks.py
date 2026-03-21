import asyncio
import threading
from datetime import date

from app.core.celery_app import celery_app
from app.crud import coupon as coupon_crud
from app.database import AsyncSessionLocal


async def _deactivate_expired_coupons_async() -> int:
    async with AsyncSessionLocal() as session:
        return await coupon_crud.deactivate_expired_coupons(session)


def _run_async(coro):
    """Run async coroutine safely from a sync Celery task context."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    # Fallback when a loop is already running in this thread.
    result: dict[str, object] = {}

    def _runner() -> None:
        try:
            result["value"] = asyncio.run(coro)
        except Exception as exc:  # pragma: no cover
            result["error"] = exc

    thread = threading.Thread(target=_runner, daemon=True)
    thread.start()
    thread.join()

    if "error" in result:
        raise result["error"]  # type: ignore[misc]
    return result.get("value")


@celery_app.task(name="app.core.tasks.deactivate_expired_coupons")
def deactivate_expired_coupons() -> dict:
    """
    Celery sync task wrapper around async DB logic.
    Marks coupons inactive when expiry < today.
    """
    updated_count = _run_async(_deactivate_expired_coupons_async())
    return {
        "run_date": date.today().isoformat(),
        "updated_count": updated_count,
    }
