from pydantic import BaseModel, HttpUrl, EmailStr, ConfigDict, Field
from datetime import datetime 

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: EmailStr | None = None


class BookmarkCreate(BaseModel):
    url: HttpUrl
    title: str
    description: str | None = None
    is_favorite: bool = False
    tag_ids: list[int] = Field(default_factory=list)


class TagCreate(BaseModel):
    name: str

class TagResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)

class BookmarkResponse(BaseModel):
    id: int
    url: str
    title: str
    description: str | None
    is_favorite: bool
    tags: list[TagResponse] = Field(default_factory=list)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class BookmarkUpdate(BaseModel):
    url: HttpUrl | None = None
    title: str | None = None
    description: str | None = None
    is_favorite: bool | None = None
    tag_ids: list[int] = Field(default_factory=list)
