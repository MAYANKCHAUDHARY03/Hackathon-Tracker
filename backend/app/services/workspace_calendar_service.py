import uuid
from datetime import datetime
from typing import List
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.hackathon import Hackathon
from app.models.round import HackathonRound, Deadline
from app.schemas.calendar import CalendarEvent

# Color mapping per event type
EVENT_COLORS = {
    "hackathon_start": "#3b82f6",       # blue-500
    "hackathon_end": "#60a5fa",          # blue-400
    "registration_deadline": "#f43f5e",  # rose-500
    "round_start": "#f59e0b",            # amber-500
    "round_end": "#fbbf24",              # amber-400
    "round_result": "#22c55e",           # green-500
    "deadline_hard": "#a855f7",          # purple-500
    "deadline_soft": "#6b7280",          # gray-500
}


class WorkspaceCalendarService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_workspace_events(
        self, workspace_id: uuid.UUID, start_date: datetime, end_date: datetime
    ) -> List[CalendarEvent]:
        events: List[CalendarEvent] = []

        # 1) Hackathon events
        hackathons_stmt = select(Hackathon).where(
            Hackathon.workspace_id == workspace_id,
            Hackathon.archived_at.is_(None),
        )
        result = await self.db.execute(hackathons_stmt)
        hackathons = result.scalars().all()

        for h in hackathons:
            if start_date <= h.start_date <= end_date:
                events.append(CalendarEvent(
                    id=f"h-start-{h.id}",
                    title=f"{h.name} — Starts",
                    description=h.description,
                    event_type="hackathon_start",
                    date=h.start_date,
                    hackathon_id=h.id,
                    hackathon_name=h.name,
                    color=EVENT_COLORS["hackathon_start"],
                ))
            if start_date <= h.end_date <= end_date:
                events.append(CalendarEvent(
                    id=f"h-end-{h.id}",
                    title=f"{h.name} — Ends",
                    description=h.description,
                    event_type="hackathon_end",
                    date=h.end_date,
                    hackathon_id=h.id,
                    hackathon_name=h.name,
                    color=EVENT_COLORS["hackathon_end"],
                ))
            if start_date <= h.registration_deadline <= end_date:
                events.append(CalendarEvent(
                    id=f"h-reg-{h.id}",
                    title=f"{h.name} — Registration Deadline",
                    description=None,
                    event_type="registration_deadline",
                    date=h.registration_deadline,
                    hackathon_id=h.id,
                    hackathon_name=h.name,
                    color=EVENT_COLORS["registration_deadline"],
                    is_hard_deadline=True,
                ))

        # 2) Round events
        rounds_stmt = select(HackathonRound).where(
            HackathonRound.workspace_id == workspace_id,
            HackathonRound.archived_at.is_(None),
        )
        result = await self.db.execute(rounds_stmt)
        rounds = result.scalars().all()

        # Build hackathon name map
        hackathon_map = {h.id: h.name for h in hackathons}

        for r in rounds:
            h_name = hackathon_map.get(r.hackathon_id, "Unknown Program")
            if r.starts_at and start_date <= r.starts_at <= end_date:
                events.append(CalendarEvent(
                    id=f"r-start-{r.id}",
                    title=f"{r.name} — Begins",
                    description=r.description,
                    event_type="round_start",
                    date=r.starts_at,
                    hackathon_id=r.hackathon_id,
                    hackathon_name=h_name,
                    color=EVENT_COLORS["round_start"],
                ))
            if r.ends_at and start_date <= r.ends_at <= end_date:
                events.append(CalendarEvent(
                    id=f"r-end-{r.id}",
                    title=f"{r.name} — Ends",
                    description=r.description,
                    event_type="round_end",
                    date=r.ends_at,
                    hackathon_id=r.hackathon_id,
                    hackathon_name=h_name,
                    color=EVENT_COLORS["round_end"],
                ))
            if r.result_at and start_date <= r.result_at <= end_date:
                events.append(CalendarEvent(
                    id=f"r-result-{r.id}",
                    title=f"{r.name} — Results",
                    description=None,
                    event_type="round_result",
                    date=r.result_at,
                    hackathon_id=r.hackathon_id,
                    hackathon_name=h_name,
                    color=EVENT_COLORS["round_result"],
                ))

        # 3) Deadline events
        deadlines_stmt = select(Deadline).where(
            Deadline.workspace_id == workspace_id,
            Deadline.archived_at.is_(None),
            and_(Deadline.due_at >= start_date, Deadline.due_at <= end_date),
        )
        result = await self.db.execute(deadlines_stmt)
        deadlines = result.scalars().all()

        for d in deadlines:
            h_name = hackathon_map.get(d.hackathon_id, "Unknown Program")
            color_key = "deadline_hard" if d.is_hard_deadline else "deadline_soft"
            events.append(CalendarEvent(
                id=f"d-{d.id}",
                title=d.name,
                description=d.description,
                event_type="deadline",
                date=d.due_at,
                hackathon_id=d.hackathon_id,
                hackathon_name=h_name,
                color=EVENT_COLORS[color_key],
                is_hard_deadline=d.is_hard_deadline,
            ))

        # Sort by date
        events.sort(key=lambda e: e.date)
        return events
