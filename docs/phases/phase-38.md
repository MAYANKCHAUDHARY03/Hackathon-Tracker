# Phase 38: Forecasting

**Status:** Completed

## Objective
Implement an AI-driven forecasting engine for projects, ensuring that all outputs are explicitly labeled as predictions and that no automated, high-impact actions are triggered without a human-in-the-loop.

## Implementation Details

- **Data Models:** Created `Forecast` model (`app/models/forecast.py`) tracking predictions, confidence, and contributing factors, with the mandatory `is_prediction=True` field.
- **Backend Components:**
  - `app/routers/forecasting.py`: REST endpoint to generate forecasts (`POST /workspaces/{workspace_id}/forecasting/projects/{project_id}`).
  - `app/services/forecasting_service.py`: Queries historical and project data and utilizes the AI Providers to generate a probability of success.
- **Frontend Components:**
  - `src/api/forecastingApi.ts`: Client for the forecasting endpoints.
  - `src/pages/Forecasting.tsx`: A dashboard that prominently flags all outputs as predictions. Added warning dialogs/information banners to inform users about the AI-nature of the data.

## Validation
- [x] AI responses contain a confidence score and factors.
- [x] Database strictly records forecasts as explicitly marked predictions.
- [x] High-impact actions are strictly decoupled from forecasting endpoints.
- [x] Visual disclaimers are present in the frontend.
