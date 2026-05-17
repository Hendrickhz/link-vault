from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_current_user, get_db
from app.models import Bookmark, User
from app.schemas import Token, BookmarkCreate, BookmarkResponse, BookmarkUpdate

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

@router.get("/", response_model=list[BookmarkResponse])
async def get_bookmarks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Bookmark).where(
            Bookmark.user_id == current_user.id
            ))
    all_bookmarks = result.scalars().all()

    return all_bookmarks
    

@router.get("/{bookmark_id}", response_model=BookmarkResponse)
async def get_bookmark_by_id(
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
    await db.refresh(bookmark)
    return bookmark

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