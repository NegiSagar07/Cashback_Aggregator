from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import authenticate_user, create_access_token, get_current_user, get_password_hash
from ..config import settings
from ..crud.user import create_user, get_user_by_username
from ..database import db_session
from ..models import User
from ..schemas import Token, UserCreate, UserRead


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, session: AsyncSession = Depends(db_session)):
	existing_user = await get_user_by_username(user_in.username, session)
	if existing_user:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")

	user = User(
		username=user_in.username,
		hashed_password=get_password_hash(user_in.password),
	)
	return await create_user(user, session)


@router.post("/token", response_model=Token)
async def login_for_access_token(
	form_data: OAuth2PasswordRequestForm = Depends(),
	session: AsyncSession = Depends(db_session),
):
	user = await authenticate_user(form_data.username, form_data.password, session)
	if not user:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Incorrect username or password",
			headers={"WWW-Authenticate": "Bearer"},
		)

	access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
	access_token = create_access_token(subject=str(user.id), expires_delta=access_token_expires)
	return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserRead)
async def read_current_user(current_user: User = Depends(get_current_user)):
	return current_user