from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .crud.user import get_user_by_id, get_user_by_username
from .database import db_session
from .models import User


pwd_context = CryptContext(
	schemes=["pbkdf2_sha256", "bcrypt"],
	deprecated="auto",
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
	return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
	return pwd_context.hash(password)


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
	expire = datetime.now(timezone.utc) + (
		expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
	)
	to_encode = {"sub": subject, "exp": expire}
	return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def authenticate_user(
	username: str,
	password: str,
	session: AsyncSession,
) -> User | None:
	user = await get_user_by_username(username, session)
	if not user or not verify_password(password, user.hashed_password):
		return None
	return user


async def get_current_user(
	token: str = Depends(oauth2_scheme),
	session: AsyncSession = Depends(db_session),
) -> User:
	credentials_exception = HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Could not validate credentials",
		headers={"WWW-Authenticate": "Bearer"},
	)

	try:
		payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
		subject = payload.get("sub")
		if subject is None:
			raise credentials_exception
		user_id = int(subject)
	except (JWTError, ValueError):
		raise credentials_exception

	user = await get_user_by_id(user_id, session)
	if user is None:
		raise credentials_exception
	if not user.is_active:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
	return user