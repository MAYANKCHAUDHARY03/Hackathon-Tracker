import uuid
from sqlalchemy import event, select
from sqlalchemy.orm import object_session
from app.models.graph import GraphEdge, EdgeProvenance
from app.models.team import Team, TeamMember
from app.models.project import Project
from app.models.challenge import Challenge
from app.models.workspace import Workspace
from app.models.hackathon import Hackathon

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
                    provenance=EdgeProvenance.verified.value,
                    confidence=1.0,
                    properties={}
                )
            )

    @event.listens_for(TeamMember, 'after_insert')
    def after_team_member_insert(mapper, connection, target):
        session = object_session(target)
        if session:
            # We need the workspace_id from the team
            team_stmt = select(Team.workspace_id).where(Team.id == target.team_id)
            result = connection.execute(team_stmt).first()
            if result:
                workspace_id = result[0]
                connection.execute(
                    GraphEdge.__table__.insert().values(
                        id=uuid.uuid4(),
                        workspace_id=workspace_id,
                        source_type="User",
                        source_id=target.user_id,
                        target_type="Team",
                        target_id=target.team_id,
                        relation_type="member_of",
                        provenance=EdgeProvenance.verified.value,
                        confidence=1.0,
                        properties={"role": target.authorization_role}
                    )
                )

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
                    provenance=EdgeProvenance.verified.value,
                    confidence=1.0,
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
                    provenance=EdgeProvenance.verified.value,
                    confidence=1.0,
                    properties={}
                )
            )

    @event.listens_for(Workspace, 'after_insert')
    def after_workspace_insert(mapper, connection, target):
        session = object_session(target)
        if session and target.organization_id:
            connection.execute(
                GraphEdge.__table__.insert().values(
                    id=uuid.uuid4(),
                    workspace_id=target.id,
                    source_type="Workspace",
                    source_id=target.id,
                    target_type="Organization",
                    target_id=target.organization_id,
                    relation_type="belongs_to",
                    provenance=EdgeProvenance.verified.value,
                    confidence=1.0,
                    properties={}
                )
            )

    from app.models.research import ResearchLink
    
    @event.listens_for(ResearchLink, 'after_insert')
    def after_research_link_insert(mapper, connection, target):
        session = object_session(target)
        if session:
            connection.execute(
                GraphEdge.__table__.insert().values(
                    id=uuid.uuid4(),
                    workspace_id=target.workspace_id,
                    source_type="Project",
                    source_id=target.project_id,
                    target_type="ResearchLink",
                    target_id=target.id,
                    relation_type="cites",
                    provenance=target.provenance,
                    confidence=1.0 if target.provenance == "verified" else 0.8,
                    properties={"type": target.type}
                )
            )
