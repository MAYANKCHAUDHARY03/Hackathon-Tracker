# Phase 37: AI Copilot

**Status:** Completed

## Objective
Implement an AI Copilot that follows a strict pipeline: User -> Intent Detection -> Permission Check -> Knowledge Graph/Search -> Verified Data -> AI Reasoning -> Answer + Evidence. It must not invent knowledge and should base its answers purely on the trusted platform data.

## Implementation Details

- **Data Models:** Uses the `CopilotQuery`, `CopilotResponse`, and `SourceEntity` schemas.
- **Backend Components:**
  - `app/routers/copilot.py`: The FastAPI router with the `/ask` endpoint.
  - `app/services/copilot_service.py`: Orchestrates the intent detection, database searching, and reasoning steps.
  - `app/services/ai/providers.py`: Integrates with AI providers (Gemini/Mock) to extract intent and generate responses.
- **Frontend Components:**
  - `src/api/copilotApi.ts`: API wrapper for `/ask` endpoint.
  - `src/pages/Copilot.tsx`: The chat interface for users to interact with the AI Copilot.

## Validation
- [x] AI reasoning is constrained by trusted data.
- [x] Every answer includes Evidence, Source Entities, Confidence, and Recommended Action.
- [x] Backend endpoint implemented and integrated in the API routes.
- [x] Frontend chat UI implemented.
