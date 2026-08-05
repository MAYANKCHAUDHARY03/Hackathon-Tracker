# Hackathon Tracker

Hackathon Tracker is a full-stack web application for tracking, organizing, and managing hackathons. Built with a React/Vite frontend and a FastAPI backend, it provides a centralized dashboard for managing events, registrations, and workspaces.

## Features (Phase 2)
- **Workspaces & Authentication**: Multi-tenant workspace isolation with secure user authentication.
- **Hackathon Management**: Full CRUD capabilities for hackathons, including registration deadlines and statuses.
- **Dashboard Summary**: Real-time aggregated statistics for upcoming, active, and completed hackathons.
- **Responsive UI**: Built with React, Tailwind CSS, and shadcn/ui.

## Project Structure
- `/` - Frontend React Application (Vite + TypeScript)
- `/backend` - Backend FastAPI Service (Python + PostgreSQL/SQLite)
- `/docs` - Architecture and phase planning documentation

## Running Locally

### Docker Compose (Recommended)
You can start the entire stack (PostgreSQL, Backend, Frontend) via Docker Compose:
```bash
docker-compose up --build
```

### Manual Setup
**Backend**:
```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

**Frontend**:
```bash
npm install
npm run dev
```

## Testing
Run the backend pytest suite:
```bash
cd backend
python -m pytest tests/
```

## Documentation
See `/docs` for detailed architectural plans, implementation phases, and API documentation.
