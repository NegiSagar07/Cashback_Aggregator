from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import User


async def get_user_by_username(username: str, session: AsyncSession) -> User | None:
	result = await session.execute(select(User).where(User.username == username))
	return result.scalar_one_or_none()


async def get_user_by_id(user_id: int, session: AsyncSession) -> User | None:
	result = await session.execute(select(User).where(User.id == user_id))
	return result.scalar_one_or_none()


async def create_user(user: User, session: AsyncSession) -> User:
	try:
		session.add(user)
		await session.commit()
		await session.refresh(user)
		return user
	except Exception:
		await session.rollback()
		raise