from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth import create_access_token, get_password_hash, verify_password
from app.dependencies import get_current_user, get_db
from app.models import User
from app.schemas import Token, UserCreate, UserResponse, UserLogin

router = APIRouter(prefix='/auth', tags=["Auth"])

@router.post("/register", response_model= UserResponse, status_code= status.HTTP_201_CREATED)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    email = user.email
    password = user.password

    result = await db.execute(select(User).where(User.email == email))
    existing_email = result.scalar_one_or_none()
    if existing_email:
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail= "Email already registered",
        )
    
    hashed_password = get_password_hash(password)

    new_user = User(
        email= email,
        hashed_password= hashed_password
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
     
    return new_user

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.email == form_data.username))
    existing_user = result.scalar_one_or_none()
    if existing_user is None:
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail= "Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

    is_verified = verify_password(form_data.password, existing_user.hashed_password)

    if not is_verified:
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail= "Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = create_access_token({"sub": existing_user.email})

    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model= UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user
