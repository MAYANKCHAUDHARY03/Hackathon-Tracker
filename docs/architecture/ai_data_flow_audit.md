# AI Data Flow Audit — Pre-Phase 28

**Date**: 2026-08-11  
**Scope**: All AI integration paths, data flows, provenance chains  
**Purpose**: Verify AI never writes to canonical tables without human action

---

## 1. Current AI Architecture

### Components
- **`AIProviderAdapter`** (abstract base): Defines `generate_project_summary`, `analyze_project_health`, `extract_search_intent`
- **`MockAIProvider`**: Deterministic fallback for testing
- **`GeminiAIProvider`**: Google Gemini 2.5 Flash integration
- **`AIProviderFactory`**: Selects provider based on config
- **`AIPrivacyFilter`**: Strips PII before sending data to AI

### Data Flow Diagram

```
User Action → API Request
       ↓
  Service Layer (reads canonical DB)
       ↓
  AIPrivacyFilter (strips PII)
       ↓
  AI Provider (Gemini/Mock)
       ↓
  AI Response (text/JSON)
       ↓
  Service Layer (formats response)
       ↓
  API Response (to user, read-only)
```

---

## 2. AI Data Access Paths

### Path 1: Project Summary Generation
```
User → POST /ai/project-summary
     → AIProviderFactory.get_provider()
     → GeminiAIProvider.generate_project_summary(project_data)
     → AIPrivacyFilter.filter_dict(project_data) ← STRIPS PII
     → Gemini API call
     → Return summary string
     → Display to user (NOT written to DB)
```
**Verdict**: ✅ AI reads filtered data, returns read-only output.

### Path 2: Project Health Analysis
```
User → POST /ai/project-health
     → GeminiAIProvider.analyze_project_health(project, tasks)
     → AIPrivacyFilter strips PII
     → Gemini API call
     → Return {health_status, risk_score, recommendations}
     → Display to user (NOT written to DB)
```
**Verdict**: ✅ AI reads filtered data, returns advisory output only.

### Path 3: Search Intent Extraction
```
User → GET /search?q=...
     → SearchService.search()
     → GeminiAIProvider.extract_search_intent(query)
     → Returns {entities, keywords}
     → Used to construct SQL WHERE clauses
     → Results fetched from canonical DB
     → Graph context hydrated from GraphEdge
```
**Verdict**: ✅ AI helps parse the query but does not write data. Search results come from canonical DB.

---

## 3. AI Write Paths — Audit

| Operation | Does AI Write to DB? | Status |
|---|---|---|
| Project summary | No — returned to user | ✅ |
| Health analysis | No — returned to user | ✅ |
| Search intent | No — used to build query only | ✅ |
| Graph edge creation | No — `graph_events.py` creates edges from model events, not AI | ✅ |
| Evaluation scoring | No — judges/people score manually | ✅ |
| Matching | No — `match_service.py` computes scores, doesn't write matches | ✅ |

**Result**: AI has NO direct write paths to any canonical table. ✅

---

## 4. V5.0 New AI Data Flows

| Phase | AI Use | Data Flow | Risk |
|---|---|---|---|
| 28 (Knowledge Graph) | AI-inferred relationship suggestions | AI suggests edges → user accepts → service creates with `provenance=AI-inferred` | **Medium** — must ensure AI suggestions are clearly labeled and require user action |
| 29 (Semantic Search) | Embedding generation | AI generates embeddings → written to `content_embeddings` table | **Low** — embeddings are derivative data, not canonical |
| 37 (AI Copilot) | Full conversational AI | AI reads Knowledge Graph + canonical data → generates answers with evidence | **High** — must enforce Evidence+Source+Confidence in every response |
| 38 (Forecasting) | Prediction generation | AI generates forecasts labeled as predictions | **Medium** — forecasts must never auto-trigger actions |

### Required Safeguards for V5.0

1. **Phase 28**: Every AI-inferred GraphEdge must carry `provenance="AI-inferred"` and `confidence` score. No AI-inferred edge can have `provenance="verified"`.

2. **Phase 34**: Hard constraint — AI can create a verification *request* but NEVER a verification *decision*. `VerificationRecord.verifier_id` must reference a human User.

3. **Phase 37**: Copilot pipeline must follow:
   ```
   User → Intent Detection → Permission Check → Knowledge Graph/Search → 
   Verified Data → AI Reasoning → Answer + Evidence
   ```
   Every response includes: `evidence`, `source_entities`, `confidence`, `recommended_action`.

4. **Phase 38**: All forecast outputs must include `is_prediction=True` flag. No forecast can trigger `AutomationRule` execution.

---

## 5. Privacy Filter Audit

The `AIPrivacyFilter` class:
- Strips fields: `email`, `password_hash`, `phone`, `ssn`, `api_key`
- Logs every AI call with: provider name, method, payload size
- Does NOT strip: `full_name`, `github_handle`, `linkedin_url`

**Recommendation for V5.0**: Add `full_name` to the default strip list when sending to external AI providers. For internal mock, it can remain.

---

## 6. Conclusion

AI data flows are **clean and read-only**. AI never writes to canonical tables. The V5.0 phases introduce new AI write paths (embeddings, relationship suggestions) that must be carefully guarded with provenance tags and human-in-the-loop verification. All safeguards are specified and will be enforced at the service layer.
