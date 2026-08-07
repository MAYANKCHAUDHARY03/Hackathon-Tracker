# Hackathon Tracker Dashboard - Operational Runbook

## Deployment Steps
1. **Frontend**: Build using `npm run build` or `vite build`. Serve `dist/` directory via Nginx or CDN.
2. **Backend**: Run using `uvicorn app.main:app --host 0.0.0.0 --port 8000`. Use process managers like Supervisor or Docker.
3. **Database**: SQLite is used for development/testing. For production, migrate to PostgreSQL by updating `DATABASE_URL` in `.env` and running `alembic upgrade head`.

## Rollback Procedures
- **Code Rollback**: Revert to the previous git tag and trigger CI/CD deployment.
- **Database Rollback**: `alembic downgrade -1` (if Alembic is configured, though current setup uses `Base.metadata.create_all`). For SQLite, restore the previous `.db` file from backups.

## Configuration References
- `VITE_API_URL`: Backend API URL (Frontend `.env`).
- `DATABASE_URL`: Connection string (Backend `.env`).
- `SECRET_KEY`: Used for JWT signing and integration encryption (Backend `.env`).
- `ENVIRONMENT`: `development` or `production` (Backend `.env`).

## Incident Playbooks
1. **Login Failures**: Check backend logs for JWT decode errors. Ensure `SECRET_KEY` is consistent.
2. **Database Locked**: If using SQLite in production under high load, database locking may occur. Consider upgrading to PostgreSQL.
3. **Integration Failures**: Check `security_vault.py` encryption/decryption keys. Ensure the key has not been rotated without re-encrypting the database.
