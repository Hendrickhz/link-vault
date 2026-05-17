from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_current_user, get_db
from app.models import Bookmark, User, BookmarkTag, Tag
from app.schemas import BookmarkCreate, BookmarkResponse, BookmarkUpdate, BookmarkListResponse
from sqlalchemy.orm import selectinload

router = APIRouter(prefix='/bookmarks', tags=["Bookmarks"])

@router.post("/", response_model=BookmarkResponse, status_code=status.HTTP_201_CREATED)
async def create_bookmark(
    bookmark: BookmarkCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    result = await db.execute(
        select(Bookmark).where(
            Bookmark.title == bookmark.title,
            Bookmark.user_id == current_user.id
            ))
    is_existing = result.scalar_one_or_none()

    if is_existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bookmark with the same title already exists"
        )
    
    new_bookmark = Bookmark(
        title = bookmark.title,
        url = str(bookmark.url),
        description = bookmark.description,
        is_favorite = bookmark.is_favorite,
        user_id = current_user.id
    )

    db.add(new_bookmark)
    await db.commit()
    await db.refresh(new_bookmark)

    return new_bookmark

@router.get("/", response_model=BookmarkListResponse)
async def get_bookmarks(
    page: int = 1,
    limit: int = 20,
    favorite: bool | None = None,
    tag: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if page < 1 or limit < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page and limit must be greater than 0",
        )

    query = (
        select(Bookmark)
        .options(selectinload(Bookmark.tags))
        .where(Bookmark.user_id == current_user.id)
    )

    count_query = (
        select(func.count())
        .select_from(Bookmark)
        .where(Bookmark.user_id == current_user.id)
    )

    if favorite is not None:
        query = query.where(Bookmark.is_favorite == favorite)
        count_query = count_query.where(Bookmark.is_favorite == favorite)

    if tag is not None:
        query = query.join(Bookmark.tags).where(
            Tag.name == tag,
            Tag.user_id == current_user.id
        ).distinct()

        count_query = (
            select(func.count(func.distinct(Bookmark.id)))
            .select_from(Bookmark)
            .join(Bookmark.tags)
            .where(
                Bookmark.user_id == current_user.id,
                Tag.name == tag,
                Tag.user_id == current_user.id,
            )
        )

    offset = (page - 1) * limit

    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    result = await db.execute(
        query.offset(offset).limit(limit)
    )
    bookmarks = result.scalars().all()

    pages = (total + limit - 1) // limit if total > 0 else 0

    return {
        "items": bookmarks,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages,
    }

@router.get("/search", response_model=BookmarkListResponse)
async def search_bookmarks(
    q:str,
    page: int = 1,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not q.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query cannot be empty",
        )

    if page < 1 or limit < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page and limit must be greater than 0",
        )
    
    query = (
        select(Bookmark)
        .options(selectinload(Bookmark.tags))
        .where(
            Bookmark.user_id == current_user.id,
            or_(
                Bookmark.title.ilike(f"%{q}%"),
                Bookmark.url.ilike(f"%{q}%"),
                Bookmark.description.ilike(f"%{q}%"),
            )
        )
    )

    count_query = (
        select(func.count())
        .select_from(Bookmark)
        .where(
            Bookmark.user_id == current_user.id,
            or_(
                Bookmark.title.ilike(f"%{q}%"),
                Bookmark.url.ilike(f"%{q}%"),
                Bookmark.description.ilike(f"%{q}%"),
            )
        )
    )

    offset = (page - 1) * limit

    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    result = await db.execute(
        query.offset(offset).limit(limit)
    )
    bookmarks = result.scalars().all()

    pages = (total + limit - 1) // limit if total > 0 else 0

    return {
        "items": bookmarks,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages,
    }


@router.get("/{bookmark_id}", response_model=BookmarkResponse)
async def get_bookmark_by_id(
    bookmark_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Bookmark).options(
            selectinload(Bookmark.tags)
        ).where(
            Bookmark.id == bookmark_id,
            Bookmark.user_id == current_user.id
            ))
    bookmark = result.scalar_one_or_none()

    if bookmark is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark Not Found"
        )
    
    return bookmark
    

@router.put("/{bookmark_id}", response_model=BookmarkResponse)
async def update_bookmark(
    bookmark_id: int,
    data: BookmarkUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Bookmark).where(
            Bookmark.id == bookmark_id,
            Bookmark.user_id == current_user.id
            ))
    bookmark = result.scalar_one_or_none()

    if bookmark is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark Not Found"
        )
    
    if data.title is not None:
        bookmark.title = data.title

    if data.url is not None:
        bookmark.url = str(data.url)

    if data.description is not None:
        bookmark.description = data.description

    # if data.tags is not None:
    #     bookmark.tags = data.tags

    if data.is_favorite is not None:
        bookmark.is_favorite = data.is_favorite

    await db.commit()
    result = await db.execute(
        select(Bookmark)
        .options(selectinload(Bookmark.tags))
        .where(
            Bookmark.id == bookmark_id,
            Bookmark.user_id == current_user.id,
        )
    )
    updated_bookmark = result.scalar_one()

    return updated_bookmark

@router.delete("/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bookmark(
    bookmark_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Bookmark).where(
            Bookmark.id == bookmark_id,
            Bookmark.user_id == current_user.id
            ))
    bookmark = result.scalar_one_or_none()

    if bookmark is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark Not Found"
        )

    await db.delete(bookmark)
    await db.commit()


@router.post("/{bookmark_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def add_tag_to_bookmark(
    bookmark_id: int,
    tag_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Bookmark).where(
            Bookmark.id == bookmark_id,
            Bookmark.user_id == current_user.id,
        )
    )
    bookmark = result.scalar_one_or_none()

    if bookmark is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found",
        )
    
    result = await db.execute(
        select(Tag).where(
            Tag.id == tag_id,
            Tag.user_id == current_user.id,
        )
    )
    tag = result.scalar_one_or_none()

    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )
    
    result = await db.execute(
        select(BookmarkTag).where(
            BookmarkTag.bookmark_id == bookmark_id,
            BookmarkTag.tag_id == tag_id,
        )
    )
    existing_link = result.scalar_one_or_none()

    if existing_link:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag already attached to bookmark",
        )
    
    link = BookmarkTag(
        bookmark_id=bookmark_id,
        tag_id=tag_id,
    )

    db.add(link)
    await db.commit()

@router.delete("/{bookmark_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_tag_from_bookmark(
    bookmark_id: int,
    tag_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Bookmark).where(
            Bookmark.id == bookmark_id,
            Bookmark.user_id == current_user.id,
        )
    )
    bookmark = result.scalar_one_or_none()

    if bookmark is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found",
        )
    
    result = await db.execute(
        select(Tag).where(
            Tag.id == tag_id,
            Tag.user_id == current_user.id,
        )
    )
    tag = result.scalar_one_or_none()

    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )
    
    result = await db.execute(
        select(BookmarkTag).where(
            BookmarkTag.bookmark_id == bookmark_id,
            BookmarkTag.tag_id == tag_id,
        )
    )
    existing_link = result.scalar_one_or_none()

    if not existing_link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag is not attached to bookmark",
        )
    
    
    await db.delete(existing_link)
    await db.commit()

@router.post("/{bookmark_id}/favorite", response_model=BookmarkResponse)
async def toggle_favorite(
    bookmark_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Bookmark).where(
            Bookmark.id == bookmark_id,
            Bookmark.user_id == current_user.id
            ))
    bookmark = result.scalar_one_or_none()

    if bookmark is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark Not Found"
        )
    
    bookmark.is_favorite = not bookmark.is_favorite
    await db.commit()
    result = await db.execute(
        select(Bookmark)
        .options(selectinload(Bookmark.tags))
        .where(
            Bookmark.id == bookmark_id,
            Bookmark.user_id == current_user.id,
        )
    )
    updated_bookmark = result.scalar_one()

    return updated_bookmark