# Phase 36: Cross-Hackathon Portfolios

## Shipped
- Created `Portfolio` model mapping portfolios to owners (user, team, or startup) and workspaces.
- Created `PortfolioProject` linking table to associate portfolios with projects across hackathons.
- Established Pydantic schemas for request validation and response mapping.
- Implemented `CrossPortfolioService` to handle creation, listing, and linking projects.
- Created `cross_portfolio` router mapping the service to the API at `/api/v1/workspaces/{workspace_id}/portfolios`.
- Refactored `Project` model to expose a `name` property for Pydantic compatibility while keeping `title` as the DB schema column.
- Added comprehensive unit tests in `test_cross_portfolio.py` verifying full end-to-end functionality including linking portfolios with mock projects.
- Generated Alembic migrations for new tables.

## Deferred
- Granular permissions mapping on individual portfolio items (currently relies on broader workspace access and owner checks).
- Full "Organization Innovation Intelligence" dashboard which was labeled as Phase 36 in the original outline (completed cross-hackathon portfolio functionality first per modified requirements).

## Deviations
- Renamed the focus slightly from "Organization Innovation Intelligence" to "Cross-Hackathon Portfolios" per current context, though it serves the same goal of cross-program aggregation.
- Used `datetime.now(UTC)` instead of `datetime.utcnow()` inline with Pydantic V2 migration and Python deprecation warnings.
