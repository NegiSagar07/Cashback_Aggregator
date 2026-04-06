from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import get_current_user
from ..database import db_session
from ..models import User
from ..services import coupon_service

router = APIRouter(tags=["Coupons"])


@router.post("/upload-coupon")
async def upload_coupon(
	file: UploadFile = File(...),
	current_user: User = Depends(get_current_user),
	session: AsyncSession = Depends(db_session),
):
	"""Uploads a coupon image, extracts details via Gemini multimodal input, and saves it."""
	if not file.content_type.startswith("image/"):
		raise HTTPException(status_code=400, detail="File must be an image (e.g., jpeg, png)")
	
	try:
		saved_coupon = await coupon_service.process_uploaded_image(file, session, current_user.id)
		return {"status": "success", "saved_coupon": saved_coupon}
	except HTTPException:
		raise
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))


@router.post("/add-coupon")
async def add_coupon(
	user_text: str,
	current_user: User = Depends(get_current_user),
	session: AsyncSession = Depends(db_session),
):
	"""Uses Gemini to turn natural language into a structured coupon object."""
	try:
		saved_coupon = await coupon_service.create_coupon_from_text(user_text, current_user.id, session)
		return {"status": "success", "saved_coupon": saved_coupon}
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommend")
async def recommend(
	platform: str,
	amount: float,
	current_user: User = Depends(get_current_user),
	session: AsyncSession = Depends(db_session),
):
	"""Finds the best coupon for the user's current shopping cart."""
	best = await coupon_service.pick_best_deal(platform, float(amount), current_user.id, session)
	if not best:
		return {
			"message": f"No valid coupons found for {platform}. Try a public code like WELCOME50!"
		}
	return {"message": "Best deal found!", "coupon": coupon_service.serialize_coupon(best)}


@router.get("/coupons")
async def list_coupons(
	current_user: User = Depends(get_current_user),
	session: AsyncSession = Depends(db_session),
):
	"""Returns all coupons stored in the database."""
	coupons = await coupon_service.get_all_coupons(current_user.id, session)
	return {"coupons": [coupon_service.serialize_coupon(c) for c in coupons]}


@router.get("/coupons/by-category")
async def list_coupons_by_category(
	category: str,
	current_user: User = Depends(get_current_user),
	session: AsyncSession = Depends(db_session),
):
	"""Returns all coupons for a given category (e.g., travel)."""
	coupons = await coupon_service.get_coupons_by_category(category, current_user.id, session)
	return {"coupons": [coupon_service.serialize_coupon(c) for c in coupons]}
