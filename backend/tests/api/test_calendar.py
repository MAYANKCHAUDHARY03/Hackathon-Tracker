import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.services.workspace_calendar_service import WorkspaceCalendarService


@pytest.fixture
def mock_hackathon():
    h = MagicMock()
    h.id = uuid4()
    h.name = "Summer Hackathon"
    h.description = "Build something cool"
    h.workspace_id = uuid4()
    now = datetime.now(timezone.utc)
    h.start_date = now + timedelta(days=5)
    h.end_date = now + timedelta(days=7)
    h.registration_deadline = now + timedelta(days=2)
    h.archived_at = None
    return h


@pytest.fixture
def mock_round(mock_hackathon):
    r = MagicMock()
    r.id = uuid4()
    r.hackathon_id = mock_hackathon.id
    r.workspace_id = mock_hackathon.workspace_id
    r.name = "Idea Submission"
    r.description = "Submit your idea"
    r.starts_at = mock_hackathon.start_date + timedelta(hours=1)
    r.ends_at = mock_hackathon.start_date + timedelta(days=1)
    r.result_at = mock_hackathon.start_date + timedelta(days=2)
    r.archived_at = None
    return r


@pytest.fixture
def mock_deadline(mock_hackathon):
    d = MagicMock()
    d.id = uuid4()
    d.hackathon_id = mock_hackathon.id
    d.workspace_id = mock_hackathon.workspace_id
    d.name = "Final Report Due"
    d.description = "Submit your final report"
    d.due_at = mock_hackathon.end_date - timedelta(hours=2)
    d.is_hard_deadline = True
    d.archived_at = None
    return d


@pytest.mark.asyncio
async def test_get_workspace_events_returns_all_event_types(mock_hackathon, mock_round, mock_deadline):
    """Service should return hackathon, round, and deadline events."""
    db = AsyncMock()

    # Mock three sequential queries
    hack_result = MagicMock()
    hack_result.scalars.return_value.all.return_value = [mock_hackathon]
    round_result = MagicMock()
    round_result.scalars.return_value.all.return_value = [mock_round]
    deadline_result = MagicMock()
    deadline_result.scalars.return_value.all.return_value = [mock_deadline]

    db.execute = AsyncMock(side_effect=[hack_result, round_result, deadline_result])

    service = WorkspaceCalendarService(db)
    now = datetime.now(timezone.utc)
    events = await service.get_workspace_events(
        mock_hackathon.workspace_id,
        now - timedelta(days=1),
        now + timedelta(days=30),
    )

    # Should have: hackathon_start, hackathon_end, registration_deadline,
    #              round_start, round_end, round_result, deadline
    event_types = [e.event_type for e in events]
    assert "hackathon_start" in event_types
    assert "hackathon_end" in event_types
    assert "registration_deadline" in event_types
    assert "round_start" in event_types
    assert "round_end" in event_types
    assert "round_result" in event_types
    assert "deadline" in event_types
    assert len(events) == 7


@pytest.mark.asyncio
async def test_events_sorted_by_date(mock_hackathon, mock_round, mock_deadline):
    """Events should be returned sorted by date."""
    db = AsyncMock()
    hack_result = MagicMock()
    hack_result.scalars.return_value.all.return_value = [mock_hackathon]
    round_result = MagicMock()
    round_result.scalars.return_value.all.return_value = [mock_round]
    deadline_result = MagicMock()
    deadline_result.scalars.return_value.all.return_value = [mock_deadline]
    db.execute = AsyncMock(side_effect=[hack_result, round_result, deadline_result])

    service = WorkspaceCalendarService(db)
    now = datetime.now(timezone.utc)
    events = await service.get_workspace_events(
        mock_hackathon.workspace_id,
        now - timedelta(days=1),
        now + timedelta(days=30),
    )

    dates = [e.date for e in events]
    assert dates == sorted(dates)


@pytest.mark.asyncio
async def test_empty_workspace_returns_no_events():
    """An empty workspace should return zero events."""
    db = AsyncMock()
    empty_result = MagicMock()
    empty_result.scalars.return_value.all.return_value = []
    db.execute = AsyncMock(return_value=empty_result)

    service = WorkspaceCalendarService(db)
    now = datetime.now(timezone.utc)
    events = await service.get_workspace_events(
        uuid4(),
        now - timedelta(days=30),
        now + timedelta(days=30),
    )
    assert events == []
