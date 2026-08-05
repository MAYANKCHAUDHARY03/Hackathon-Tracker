# Stage 2: Submission Domain Foundation Report

## Implementation Details

We have extended the base data model to support team submissions tailored to Hackathon Rounds.

### `SubmissionRequirement` model
Added to `app/models/submission.py`. Defines what teams need to submit during a specific round.
- `round_id`, `sequence`
- `requirement_type`: Categorical tracking (e.g. `url`, `github_url`, `text`)
- `validation_rules`: Extensible JSON column for dynamic frontend validations.
- `is_required`: Determines hard completion metrics.

### `RoundSubmission` model
Added to `app/models/submission.py`. Represents the master record of a team's submission for a round.
- `team_id`, `round_id`, `status` (`draft`, `submitted`, `locked`)
- `snapshot`: A JSON column serving as an immutable point-in-time record of the final submission, protecting against subsequent changes to related data models.

### `SubmissionItem` model
Added to `app/models/submission.py`. Captures individual entries mapped directly against `SubmissionRequirement` objects.
- `submission_id`, `requirement_id`
- `content`: Text payload (URLs, markdown, etc.)
- `is_valid`: Boolean evaluation state flag, maintained independently of overall status.

### Migrations
- Migration `641419d1654a_add_submission_models` generated and applied successfully against SQLite `test.db`.

## Verification
- Applied Alembic migration `upgrade head` effectively.
- Tested SQLite schema integrity without constraint violations.

## Next Steps
Proceeding to Stage 3: Backend APIs and Authorization to build business logic enforcing submission locking, state transitions, and server-side readiness calculation.
