from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_current_user, get_db
from app.models import Tag, User
from app.schemas import TagCreate, TagResponse, TagUpdate

router = APIRouter(prefix='/tags', tags=["Tags"])

@router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    data: TagCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    result = await db.execute(
        select(Tag).where(
            Tag.name == data.name,
            Tag.user_id == current_user.id
            ))
    is_existing = result.scalar_one_or_none()

    if is_existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag with the same name already exists"
        )
    
    new_tag = Tag(
        name = data.name,
        user_id = current_user.id
    )

    db.add(new_tag)
    await db.commit()
    await db.refresh(new_tag)

    return new_tag

@router.get("/", response_model=list[TagResponse])
async def get_tags(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Tag).where(
            Tag.user_id == current_user.id
            ))
    all_tags = result.scalars().all()

    return all_tags
    

@router.get("/{tag_id}", response_model=TagResponse)
async def get_tag_by_id(
    tag_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Tag).where(
            Tag.id == tag_id,
            Tag.user_id == current_user.id
            ))
    tag = result.scalar_one_or_none()

    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag Not Found"
        )
    
    return tag
    

@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: int,
    data: TagUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Tag).where(
            Tag.id == tag_id,
            Tag.user_id == current_user.id
            ))
    tag = result.scalar_one_or_none()

    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag Not Found"
        )
    
    result = await db.execute(
        select(Tag).where(
            Tag.name == data.name,
            Tag.user_id == current_user.id,
            Tag.id != tag_id,
        )
    )
    existing_tag = result.scalar_one_or_none()

    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag with the same name already exists",
        )
    
    tag.name = data.name

    await db.commit()
    await db.refresh(tag)
    return tag

@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Tag).where(
            Tag.id == tag_id,
            Tag.user_id == current_user.id
            ))
    tag = result.scalar_one_or_none()

    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag Not Found"
        )

    await db.delete(tag)
    await db.commit()