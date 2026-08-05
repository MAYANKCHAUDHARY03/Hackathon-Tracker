# Stage 1: Round and Deadline Domain Report

## Implementation Details

We have extended the base data model to support timezone-aware Hackathons and structured Rounds/Deadlines.

### `Hackathon` updates
- Added `timezone: Mapped[str] = mapped_column(String, nullable=False, default="UTC")`
- Modified existing `start_date` and `end_date` indices to correctly index timeline querying.

### `HackathonRound` model
Added to `app/models/round.py`. Captures the structured sequence of phases during a hackathon (e.g., Registration, Idea Submission, Final Demo).
- `hackathon_id`, `sequence`, `status`
- Unique constraint on `(hackathon_id, sequence)` ensures ordering integrity.

### `Deadline` model
Added to `app/models/round.py`. Tracks important dates that may or may not be tied strictly to a round.
- `due_at` (timezone aware)
- `is_hard_deadline` determines whether late submissions are forcefully rejected.

### `RoundProgress` model
Added to `app/models/round.py`. Represents a Team's progression through a specific HackathonRound.
- `status` (`not_started`, `draft`, `submitted`, `evaluated`)
- `score` and `feedback` for review processing.

### Migrations
- Migration `035fcd8f66d7_add_rounds_and_deadlines` generated and successfully applied to upgrade the SQLite database schema (`test.db`).

## Verification
- Applied Alembic migration `upgrade head` effectively.
- Tested SQLite schema integrity.

## Next Steps
Proceeding to Stage 2: Submission Domain Foundation to create models for Submission Requirements and Submission Items.
