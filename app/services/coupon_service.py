from sqlalchemy.ext.asyncio import AsyncSession

from ..crud import coupon as coupon_crud
from ..models import Coupon
from .ai_service import parse_coupon_from_text


def serialize_coupon(coupon: Coupon) -> dict:
	return {
		"id": coupon.id,
		"platform": coupon.platform,
		"discount_type": coupon.discount_type,
		"value": coupon.value,
		"min_spend": coupon.min_spend,
		"expiry": str(coupon.expiry),
		"category": coupon.category,
		"user_id": coupon.user_id,
	}


def _estimate_savings(coupon: Coupon, amount: float) -> float:
	if coupon.discount_type == "percentage":
		return (coupon.value / 100.0) * amount
	return coupon.value


async def create_coupon_from_text(user_text: str, user_id: int, session: AsyncSession) -> dict:
	coupon = parse_coupon_from_text(user_text)
	coupon.user_id = user_id
	saved_coupon = await coupon_crud.create_coupon(coupon, session)
	return serialize_coupon(saved_coupon)


async def pick_best_deal(platform: str, amount: float, user_id: int, session: AsyncSession):
	eligible = await coupon_crud.get_eligible_coupons(platform, amount, user_id, session)

	if not eligible:
		return None

	return max(eligible, key=lambda c: _estimate_savings(c, amount))


async def get_all_coupons(user_id: int, session: AsyncSession):
	return await coupon_crud.get_all_coupons(user_id, session)
