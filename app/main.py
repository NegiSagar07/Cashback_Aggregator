from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from .api.auth import router as auth_router
from .auth import get_current_user
from .api.coupon import router as coupon_router
from .database import db_session
from .models import User

# Initialize FastAPI
app = FastAPI(title="Smart Coupon Saver V2.1")
app.include_router(auth_router)
app.include_router(coupon_router)


@app.get("/health/db", tags=["Health"])
async def database_health(
	current_user: User = Depends(get_current_user),
	session: AsyncSession = Depends(db_session),
):
	try:
		await session.execute(text("SELECT 1"))
		return {"status": "ok", "database": "reachable"}
	except Exception as exc:
		raise HTTPException(
			status_code=503,
			detail={"status": "error", "database": "unreachable", "reason": str(exc)},
		) from exc
