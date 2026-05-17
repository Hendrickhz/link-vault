import asyncio

from sqlalchemy import select

from app.auth import get_password_hash
from app.database import AsyncSessionLocal, Base, engine
from app.models import Bookmark, BookmarkTag, Tag, User
import app.models  # noqa: F401 - ensure models are registered for create_all


DEMO_USERS = [
    {
        "email": "demo@example.com",
        "password": "demo1234",
        "tags": ["python", "backend", "docs"],
        "bookmarks": [
            {
                "title": "FastAPI Docs",
                "url": "https://fastapi.tiangolo.com",
                "description": "Official FastAPI documentation.",
                "is_favorite": True,
                "tags": ["python", "backend", "docs"],
            },
            {
                "title": "SQLAlchemy Async Guide",
                "url": "https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html",
                "description": "Async ORM patterns with SQLAlchemy 2.",
                "is_favorite": False,
                "tags": ["python", "backend", "docs"],
            },
            {
                "title": "Pydantic",
                "url": "https://docs.pydantic.dev/latest/",
                "description": "Validation and settings management in Python.",
                "is_favorite": True,
                "tags": ["python", "docs"],
            },
        ],
    },
    {
        "email": "reader@example.com",
        "password": "reader1234",
        "tags": ["reading", "reference"],
        "bookmarks": [
            {
                "title": "Real Python",
                "url": "https://realpython.com/",
                "description": "Python tutorials and articles.",
                "is_favorite": False,
                "tags": ["reading", "reference"],
            },
            {
                "title": "MDN Web Docs",
                "url": "https://developer.mozilla.org/",
                "description": "Reference docs for web technologies.",
                "is_favorite": True,
                "tags": ["reference"],
            },
        ],
    },
]


async def ensure_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_or_create_user(session, email: str, password: str) -> User:
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is not None:
        return user

    user = User(email=email, hashed_password=get_password_hash(password))
    session.add(user)
    await session.flush()
    return user


async def get_or_create_tag(session, user_id: int, name: str) -> Tag:
    result = await session.execute(
        select(Tag).where(Tag.user_id == user_id, Tag.name == name)
    )
    tag = result.scalar_one_or_none()
    if tag is not None:
        return tag

    tag = Tag(user_id=user_id, name=name)
    session.add(tag)
    await session.flush()
    return tag


async def get_or_create_bookmark(session, user_id: int, data: dict) -> Bookmark:
    result = await session.execute(
        select(Bookmark).where(Bookmark.user_id == user_id, Bookmark.title == data["title"])
    )
    bookmark = result.scalar_one_or_none()
    if bookmark is not None:
        return bookmark

    bookmark = Bookmark(
        user_id=user_id,
        title=data["title"],
        url=data["url"],
        description=data["description"],
        is_favorite=data["is_favorite"],
    )
    session.add(bookmark)
    await session.flush()
    return bookmark


async def attach_tag(session, bookmark_id: int, tag_id: int) -> None:
    result = await session.execute(
        select(BookmarkTag).where(
            BookmarkTag.bookmark_id == bookmark_id,
            BookmarkTag.tag_id == tag_id,
        )
    )
    existing_link = result.scalar_one_or_none()
    if existing_link is not None:
        return

    session.add(BookmarkTag(bookmark_id=bookmark_id, tag_id=tag_id))
    await session.flush()


async def seed() -> None:
    await ensure_tables()

    async with AsyncSessionLocal() as session:
        for user_data in DEMO_USERS:
            user = await get_or_create_user(
                session, user_data["email"], user_data["password"]
            )

            tag_map: dict[str, Tag] = {}
            for tag_name in user_data["tags"]:
                tag_map[tag_name] = await get_or_create_tag(session, user.id, tag_name)

            for bookmark_data in user_data["bookmarks"]:
                bookmark = await get_or_create_bookmark(session, user.id, bookmark_data)
                for tag_name in bookmark_data["tags"]:
                    await attach_tag(session, bookmark.id, tag_map[tag_name].id)

        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed())
    print("Seed data created.")
