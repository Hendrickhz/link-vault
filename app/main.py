from fastapi import FastAPI
from app.routers import auth, bookmarks, tags
from app.database import Base, engine
import app.models

app = FastAPI(
    title="LinkVault API",
    description="A personal bookmark manager REST API with JWT authentication.",
    version="1.0.0",
)
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
app.include_router(auth.router)
app.include_router(bookmarks.router)
app.include_router(tags.router)

