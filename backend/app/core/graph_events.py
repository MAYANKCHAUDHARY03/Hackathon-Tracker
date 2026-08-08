import uuid
from sqlalchemy import event
from sqlalchemy.orm import object_session
from app.models.graph import GraphEdge
from app.models.team import Team, TeamMember
from app.models.project import Project
from app.models.challenge import Challenge
from app.models.hackathon import Hackathon
from app.models.people import MentorAssignment

def register_graph_events():
    @event.listens_for(Team, 'after_insert')
    def after_team_insert(mapper, connection, target):
        session = object_session(target)
        if session:
            connection.execute(
                GraphEdge.__table__.insert().values(
                    id=uuid.uuid4(),
                    workspace_id=target.workspace_id,
                    source_type="Hackathon",
                    source_id=target.hackathon_id,
                    target_type="Team",
                    target_id=target.id,
                    relation_type="contains",
                    properties={}
                )
            )

    @event.listens_for(TeamMember, 'after_insert')
    def after_team_member_insert(mapper, connection, target):
        session = object_session(target)
        if session:
            # Team -> contains -> User
            # Wait, TeamMember doesn't have workspace_id, we can get it from team.
            # But the event doesn't eagerly load target.team.
            # For simplicity, we can fetch workspace_id via session, or just skip it if we don't have it right away?
            pass # Skipping for now to avoid implicit IO in sync event

    @event.listens_for(Project, 'after_insert')
    def after_project_insert(mapper, connection, target):
        session = object_session(target)
        if session:
            connection.execute(
                GraphEdge.__table__.insert().values(
                    id=uuid.uuid4(),
                    workspace_id=target.workspace_id,
                    source_type="Team",
                    source_id=target.team_id,
                    target_type="Project",
                    target_id=target.id,
                    relation_type="created",
                    properties={}
                )
            )
    @event.listens_for(Challenge, 'after_insert')
    def after_challenge_insert(mapper, connection, target):
        session = object_session(target)
        if session:
            connection.execute(
                GraphEdge.__table__.insert().values(
                    id=uuid.uuid4(),
                    workspace_id=target.workspace_id,
                    source_type="Hackathon",
                    source_id=target.hackathon_id,
                    target_type="Challenge",
                    target_id=target.id,
                    relation_type="contains",
                    properties={}
                )
            )
