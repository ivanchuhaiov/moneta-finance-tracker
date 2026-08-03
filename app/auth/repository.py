from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def get_user_by_email(email: str, db: AsyncSession) -> User | None:
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_username(username: str, db: AsyncSession) -> User | None:
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_google_id(google_id: str, db: AsyncSession) -> User | None:
    stmt = select(User).where(User.google_id == google_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_user(user: User, db: AsyncSession) -> User:
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def link_google_account(user: User, google_id: str, db: AsyncSession) -> User:
    user.google_id = google_id
    await db.commit()
    await db.refresh(user)
    return user