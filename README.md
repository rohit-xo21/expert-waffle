# Simple Social (FastAPI + Streamlit)

A small, minimal social-media backend + frontend built with FastAPI (backend) and Streamlit (frontend). The backend provides user authentication (fastapi-users), file uploads (ImageKit integration), and a simple posts/feed API stored in a local SQLite database. The frontend is a compact Streamlit app that provides login/register, upload, and feed views.

## Quick description

- Backend: FastAPI application in `app/`.
  - Auth powered by `fastapi-users` (JWT auth).
  - Async SQLAlchemy (SQLite `test.db`) for users and posts.
  - Upload endpoint (`/upload`) that stores metadata in `posts` and uploads files through ImageKit.
  - Feed endpoint: `GET /feed` returns posts with author email and ownership flag.

- Frontend: `frontend.py` (Streamlit)
  - Simple, minimal UI for login/register, upload, and browsing the feed.
  - Gracefully handles backend connection errors and displays helpful messages.

## Project layout

- `app/` - backend package
  - `app/app.py` - FastAPI application and routes
  - `app/db.py` - SQLAlchemy models, session and db helpers
  - `app/users.py` - fastapi-users setup and manager
  - other modules: images, schemas, etc.

- `frontend.py` - Streamlit UI
- `.venv/` - (recommended) virtual environment
- `test.db` - SQLite DB created automatically by the app

## Requirements (recommended)

- Python 3.11 (recommended for best compatibility on Windows)
- pip, virtualenv or venv

Notes: Some binary packages (for example `pyarrow`) may not have prebuilt wheels for newer Python versions; if you hit build errors when installing dependencies, switch to Python 3.11 or use conda/Miniforge which often provides prebuilt packages.

## Setup (Windows)

1. Create a virtualenv and activate it (PowerShell/Git Bash paths shown):

```bash
# recommended: create a new venv with a stable Python (3.11)
py -3.11 -m venv .venv
# Activate (PowerShell)
.\.venv\Scripts\Activate.ps1
# or (Git Bash / bash)
source .venv/Scripts/activate
```

2. Upgrade pip & install dependencies (adjust if you have a `requirements.txt`):

```bash
python -m pip install --upgrade pip setuptools wheel
python -m pip install fastapi uvicorn fastapi-users[sqlalchemy] fastapi-users-db-sqlalchemy sqlalchemy aiosqlite imagekitio requests streamlit
```

If the installer tries to build `pyarrow` and fails (CMake / build tools error), either:
- Use Python 3.11 (recommended), or
- Install `conda`/`mambaforge` and install packages from `conda-forge`.

## Run (development)

Open two terminals.

1) Start the backend (FastAPI/uvicorn):

```bash
python -m uvicorn app.app:app --reload
```

- API docs (interactive): http://127.0.0.1:8000/docs

2) Start the frontend (Streamlit):

```bash
python -m streamlit run frontend.py
```

Streamlit will open a local URL (usually `http://localhost:8501`) where you can try the app.

## Important endpoints

- POST `/auth/register` - register a new user
- POST `/auth/jwt/login` - login (form data username & password)
- GET `/users/me` - get current user
- POST `/upload` - upload a file (multipart form: `file`, `caption`)
- GET `/feed` - get feed with posts
- DELETE `/post/{post_id}` - delete a post (owner only)

## Database

The app uses SQLite (`test.db`) in the project root by default. The DB and tables are created automatically at startup via `create_db_and_tables()` called during the FastAPI app lifespan.



