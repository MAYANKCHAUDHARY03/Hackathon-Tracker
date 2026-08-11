# Phase 33: Innovation Data Exchange

## Overview
This phase implements versioned schemas and the infrastructure for exporting and importing core Hackathon Tracker entities (Hackathons, Projects, Organizations) in multiple formats (JSON, NDJSON, and CSV).

## What Shipped
- `InnovationSchemaV1` schema definition for data exchange.
- `DataExchangeService` that supports querying entities scoped by workspace and generating responses in JSON, NDJSON (newline-delimited JSON), and CSV (zipped) formats.
- API endpoints `GET /api/v1/exchange/export` and `POST /api/v1/exchange/import` protected by `get_api_key` and scoped OAuth dependencies.
- Pytest coverage for the JSON, NDJSON, and CSV exports to verify correct mapping and formatting.

## Deviations / Notes
- The import logic creates new Hackathons inside the current workspace. Project and Organization imports are stubbed/deferred to a future synchronization mechanism to handle complex ID mapping/conflict resolution across instances.
- CSV export returns a Zip file containing multiple CSVs (one per entity type) rather than a single CSV, because the schemas represent distinct hierarchical entities.

## Next Step
Automatically progressing to **Phase 34 - Trust & Verification Network**.
