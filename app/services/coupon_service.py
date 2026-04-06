from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile, HTTPException

from ..crud import coupon as coupon_crud
from ..models import Coupon
from .ai_service import parse_coupon_from_text, extract_coupon_from_image
import json


def serialize_coupon(coupon: Coupon) -> dict:
	return {
		"id": coupon.id,
		"platform": coupon.platform,
		"discount_type": coupon.discount_type,
		"value": coupon.value,
		"min_spend": coupon.min_spend,
		"max_cap": coupon.max_cap,
		"is_active": coupon.is_active,
		"expiry": str(coupon.expiry),
		"category": coupon.category,
		"user_id": coupon.user_id,
	}


def _estimate_savings(coupon: Coupon, amount: float) -> float:
	if coupon.discount_type == "percentage":
		estimated = (coupon.value / 100.0) * amount
		if coupon.max_cap is not None:
			return min(estimated, coupon.max_cap)
		return estimated
	return coupon.value


async def create_coupon_from_text(user_text: str, user_id: int, session: AsyncSession) -> dict:
	coupon = parse_coupon_from_text(user_text)
	coupon.user_id = user_id
	saved_coupon = await coupon_crud.create_coupon(coupon, session)
	return serialize_coupon(saved_coupon)


async def process_uploaded_image(file: UploadFile, session: AsyncSession, user_id: int) -> dict:
	try:
		image_bytes = await file.read()
	except Exception as e:
		raise HTTPException(status_code=400, detail=f"Failed to read image bytes: {str(e)}")

	try:
		coupon_data = await extract_coupon_from_image(image_bytes)
	except json.JSONDecodeError:
		raise HTTPException(status_code=400, detail="AI returned malformed JSON.")
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"AI image parsing failed: {str(e)}")

	# Convert CouponCreate to Coupon model
	coupon_obj = Coupon(
		platform=coupon_data.platform,
		discount_type=coupon_data.discount_type.value if hasattr(coupon_data.discount_type, 'value') else coupon_data.discount_type,
		value=coupon_data.value,
		min_spend=coupon_data.min_spend,
		max_cap=coupon_data.max_cap,
		expiry=coupon_data.expiry,
		category=coupon_data.category.value if hasattr(coupon_data.category, 'value') else coupon_data.category,
		user_id=user_id
	)
	saved_coupon = await coupon_crud.create_coupon(coupon_obj, session)
	return serialize_coupon(saved_coupon)


async def pick_best_deal(platform: str, amount: float, user_id: int, session: AsyncSession):
	eligible = await coupon_crud.get_eligible_coupons(platform, amount, user_id, session)

	if not eligible:
		return None

	return max(eligible, key=lambda c: _estimate_savings(c, amount))


async def get_all_coupons(user_id: int, session: AsyncSession):
	return await coupon_crud.get_all_coupons(user_id, session)


async def get_coupons_by_category(category: str, user_id: int, session: AsyncSession):
	normalized_category = category.strip().capitalize()
	return await coupon_crud.get_coupons_by_category(normalized_category, user_id, session)
