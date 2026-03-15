from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import db_session
from ..services import coupon_service

router = APIRouter(tags=["Coupons"])


@router.post("/add-coupon")
async def add_coupon(user_text: str, session: AsyncSession = Depends(db_session)):
	"""Uses Gemini to turn natural language into a structured coupon object."""
	try:
		saved_coupon = await coupon_service.create_coupon_from_text(user_text, session)
		return {"status": "success", "saved_coupon": saved_coupon}
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommend")
async def recommend(platform: str, amount: float, session: AsyncSession = Depends(db_session)):
	"""Finds the best coupon for the user's current shopping cart."""
	best = await coupon_service.pick_best_deal(platform, float(amount), session)
	if not best:
		return {
			"message": f"No valid coupons found for {platform}. Try a public code like WELCOME50!"
		}
	return {"message": "Best deal found!", "coupon": coupon_service.serialize_coupon(best)}


@router.get("/coupons")
async def list_coupons(session: AsyncSession = Depends(db_session)):
	"""Returns all coupons stored in the database."""
	coupons = await coupon_service.get_all_coupons(session)
	return {"coupons": [coupon_service.serialize_coupon(c) for c in coupons]}
