from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.auth.schemas import UserCreate, UserResponse, LoginRequest, TokenResponse, RefreshRequest, GoogleAuthRequest
from app.auth.security import hash_password, verify_password, create_access_token, create_refresh_token,decode_token
from app.auth.dependencies import get_current_user
from app.models.user import User
from sqlalchemy import select
from jose import JWTError
from app.auth.google_oauth import exchange_code_for_token, get_google_user_info


router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == user_data.email)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )

    stmt = select(User).where(User.username == user_data.username)
    result = await db.execute(stmt)
    existing_username = result.scalar_one_or_none()

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

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == credentials.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

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

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)



@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
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

    return TokenResponse(access_token=new_access_token, refresh_token=new_refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user



@router.post("/google", response_model=TokenResponse)
async def google_auth(payload: GoogleAuthRequest, db: AsyncSession = Depends(get_db)):
    google_access_token = await exchange_code_for_token(payload.code)
    user_info = await get_google_user_info(google_access_token)

    email = user_info["email"]
    google_id = user_info["sub"]

    # Шаг 1: ищем юзера по google_id
    stmt = select(User).where(User.google_id == google_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is not None:
        # нашли юзера, который уже логинился через Google раньше — просто выдаём токены
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    # Шаг 2: юзера с таким google_id нет — ищем по email
    # (вдруг он уже регистрировался обычным способом раньше)
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is not None:
        # юзер существует, но пока без привязки к Google — привязываем
        user.google_id = google_id
        await db.commit()
        await db.refresh(user)

    else:
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

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        user = new_user


    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)