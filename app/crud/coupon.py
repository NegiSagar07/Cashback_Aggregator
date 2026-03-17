from datetime import date

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Coupon


async def create_coupon(coupon: Coupon, session: AsyncSession) -> Coupon:
	try:
		session.add(coupon)
		await session.commit()
		await session.refresh(coupon)
		return coupon
	except Exception:
		await session.rollback()
		raise


async def get_eligible_coupons(
	platform: str,
	amount: float,
	user_id: int,
	session: AsyncSession,
) -> list[Coupon]:
	today = date.today()

	result = await session.execute(
		select(Coupon).where(
			Coupon.user_id == user_id,
			Coupon.platform.ilike(platform),
			Coupon.expiry >= today,
			or_(Coupon.min_spend.is_(None), Coupon.min_spend <= amount),
		)
	)
	return result.scalars().all()


async def get_all_coupons(user_id: int, session: AsyncSession):
	result = await session.execute(select(Coupon).where(Coupon.user_id == user_id))
	return result.scalars().all()


async def get_coupons_by_category(
	category: str,
	user_id: int,
	session: AsyncSession,
) -> list[Coupon]:
	result = await session.execute(
		select(Coupon).where(
			Coupon.user_id == user_id,
			Coupon.category.ilike(category),
		)
	)
	return result.scalars().all()
