from fastapi import HTTPException, status
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import repository
from app.auth.google_oauth import exchange_code_for_token, get_google_user_info
from app.auth.schemas import UserCreate, LoginRequest, RefreshRequest, GoogleAuthRequest
from app.auth.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.models.user import User


async def register_user(user_data: UserCreate, db: AsyncSession) -> User:
    existing_user = await repository.get_user_by_email(str(user_data.email), db)

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )

    existing_username = await repository.get_user_by_username(user_data.username, db)

    if existing_username is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )

    hashed_password = hash_password(user_data.password)

    new_user = User(
        email=str(user_data.email),
        username=user_data.username,
        firstname=user_data.firstname,
        lastname=user_data.lastname,
        hashed_password=hashed_password,
        role="user",
        status="active",
    )

    return await repository.create_user(new_user, db)


async def login_user(credentials: LoginRequest, db: AsyncSession) -> tuple[str, str]:
    user = await repository.get_user_by_email(str(credentials.email), db)

    if user is None or user.hashed_password is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    return access_token, refresh_token


async def refresh_tokens(payload: RefreshRequest, db: AsyncSession) -> tuple[str, str]:
    try:
        decoded = decode_token(payload.refresh_token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    if decoded.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is not a refresh token",
        )

    user_id = int(decoded.get("sub"))
    user = await db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    new_access_token = create_access_token(user.id)
    new_refresh_token = create_refresh_token(user.id)

    return new_access_token, new_refresh_token


async def authenticate_google(payload: GoogleAuthRequest, db: AsyncSession) -> tuple[str, str]:
    google_access_token = await exchange_code_for_token(payload.code)
    user_info = await get_google_user_info(google_access_token)

    email = user_info["email"]
    google_id = user_info["sub"]

    user = await repository.get_user_by_google_id(google_id, db)

    if user is None:
        user = await repository.get_user_by_email(email, db)

    if user is None:
        user = await _create_google_user(email, google_id, user_info, db)
    elif user.google_id is None:
        user = await repository.link_google_account(user, google_id, db)

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    return access_token, refresh_token


async def _create_google_user(email: str, google_id: str, user_info: dict, db: AsyncSession) -> User:
    given_name = user_info.get("given_name", "")
    family_name = user_info.get("family_name", "")
    username = email.split("@")[0]

    new_user = User(
        email=email,
        username=username,
        firstname=given_name,
        lastname=family_name,
        hashed_password=None,
        google_id=google_id,
        role="user",
        status="active",
    )

    return await repository.create_user(new_user, db)