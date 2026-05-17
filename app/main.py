from fastapi import FastAPI
from app.routers import auth, bookmarks, tags
from app.database import Base, engine

app = FastAPI(
    title="LinkVault API",
    description=(
        "A personal bookmark manager REST API with JWT authentication, tagging, "
        "search, filtering, favorites, and pagination.\n\n"
        "Demo data:\n"
        "- Demo user: `demo@example.com` / `demo1234`\n"
        "- Demo user: `reader@example.com` / `reader1234`"
    ),
    version="1.0.0",
)
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
app.include_router(auth.router)
app.include_router(bookmarks.router)
app.include_router(tags.router)

