# LinkVault API

LinkVault is a personal bookmark manager REST API built with FastAPI. It supports JWT authentication, bookmark CRUD, tag organization, search, filtering, favorites, and pagination. The built-in Swagger UI at `/docs` acts as the live interactive demo.

## Features

- User registration and login with JWT bearer authentication
- Protected user profile endpoint
- Bookmark create, read, update, and delete
- Tag create, list, update, and delete
- Attach and remove tags from bookmarks
- Search bookmarks by title, URL, or description
- Filter bookmarks by tag and favorite status
- Paginated bookmark listing
- Auto-generated OpenAPI docs via Swagger UI

## Tech Stack

- FastAPI
- Pydantic v2
- SQLAlchemy async
- SQLite for local development
- JWT via `python-jose`
- Password hashing via `passlib`

## Project Structure

```text
LinkVault/
├── app/
│   ├── auth.py
│   ├── database.py
│   ├── dependencies.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   └── routers/
│       ├── auth.py
│       ├── bookmarks.py
│       └── tags.py
├── config.py
├── requirements.txt
└── README.md
```

## Local Setup

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies.
4. Create a `.env` file.
5. Run the app with Uvicorn.

### Create Virtual Environment

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Install Dependencies

```powershell
pip install -r requirements.txt
```

## Environment Variables

Create `.env` with:

```env
SECRET_KEY=replace-with-a-long-random-secret
DATABASE_URL=sqlite+aiosqlite:///./linkvault.db
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Run The API

```powershell
uvicorn app.main:app --reload
```

Then open:

- `http://127.0.0.1:8000/docs`

## Seed Demo Data

To populate the database with demo users, tags, bookmarks, and bookmark-tag links:

```powershell
python seed.py
```

Demo users created by the seeder:

- `demo@example.com` / `demo1234`
- `reader@example.com` / `reader1234`

## API Overview

### Auth

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`

### Bookmarks

- `GET /bookmarks`
- `GET /bookmarks/search`
- `POST /bookmarks`
- `GET /bookmarks/{bookmark_id}`
- `PUT /bookmarks/{bookmark_id}`
- `DELETE /bookmarks/{bookmark_id}`
- `POST /bookmarks/{bookmark_id}/favorite`
- `POST /bookmarks/{bookmark_id}/tags/{tag_id}`
- `DELETE /bookmarks/{bookmark_id}/tags/{tag_id}`

### Tags

- `GET /tags`
- `POST /tags`
- `GET /tags/{tag_id}`
- `PUT /tags/{tag_id}`
- `DELETE /tags/{tag_id}`

## Auth Flow

1. Register a user with `POST /auth/register`.
2. Log in with `POST /auth/login`.
3. Copy the returned bearer token.
4. Authorize in Swagger UI.
5. Call protected endpoints like `/auth/me` or `/bookmarks`.

## Notes

- SQLite is used locally for simplicity.
- The app currently creates tables on startup with SQLAlchemy `create_all()`.
- A production-ready next step would be Alembic migrations plus PostgreSQL deployment.

## Future Improvements

- Alembic migrations
- PostgreSQL deployment configuration
- Better uniqueness constraints at the database level
- Rate limiting
- Redis caching
- Full-text search
- Tests and CI pipeline
