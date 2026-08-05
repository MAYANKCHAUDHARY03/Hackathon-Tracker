# Hackathon Tracker Backend

FastAPI backend service for the Hackathon Tracker application.

## Tech Stack
- **Framework**: FastAPI
- **Database**: PostgreSQL (Production/Docker) / SQLite (Local Dev/Tests)
- **ORM**: SQLAlchemy 2.0 (Async)
- **Migrations**: Alembic
- **Testing**: Pytest with `pytest-asyncio`

## Setup

1. Create a virtual environment and activate it:
```bash
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On Linux/Mac
source .venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Setup environment variables by copying `.env.example` to `.env`:
```bash
cp .env.example .env
```

4. Run database migrations:
```bash
alembic upgrade head
```

5. Start the development server:
```bash
uvicorn app.main:app --reload
```

## Database Migrations
To generate a new migration after updating models:
```bash
alembic revision --autogenerate -m "Description of changes"
```

To run tests (uses an isolated in-memory SQLite database):
```bash
pytest tests/
```
