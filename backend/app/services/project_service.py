import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.project import Project
from app.schemas.project import ProjectCreate
from app.models.user import User
from app.models.kanban import KanbanBoard, KanbanColumn
from app.services.graph_service import KnowledgeGraphService
from datetime import datetime

async def get_projects(db: AsyncSession, workspace_id: uuid.UUID):
    stmt = select(Project).where(Project.workspace_id == workspace_id)
    result = await db.execute(stmt)
    return result.scalars().all()

async def create_project(db: AsyncSession, workspace_id: uuid.UUID, team_id: uuid.UUID, project_in: ProjectCreate, user: User):
    import re
    slug = re.sub(r'[^a-z0-9]+', '-', project_in.name.lower()).strip('-')
    project = Project(
        workspace_id=workspace_id,
        team_id=team_id,
        title=project_in.name,
        slug=slug,
        description=project_in.description,
        repository_url=project_in.repository_url,
        hackathon_id=project_in.hackathon_id
    )
    db.add(project)
    
    # We must explicitly flush so the project gets an ID before we can create a board
    await db.flush()

    # Automatically create a KanbanBoard for the new Project
    board = KanbanBoard(
        workspace_id=workspace_id,
        project_id=project.id,
        name=f"{project.title} Board"
    )
    db.add(board)
    await db.flush()

    # Create default columns
    default_columns = [
        ("Todo", 1000.0),
        ("In Progress", 2000.0),
        ("Done", 3000.0)
    ]
    for name, pos in default_columns:
        col = KanbanColumn(
            board_id=board.id,
            name=name,
            position=pos
        )
        db.add(col)

    await db.commit()
    await db.refresh(project)
    
    # Initialize the project state as IDEA in the graph
    await transition_project_state(db, workspace_id, project.id, "IDEA", user)
    
    return project

async def transition_project_state(db: AsyncSession, workspace_id: uuid.UUID, project_id: uuid.UUID, new_state: str, user: User, notes: str = ""):
    # Validate project exists
    stmt = select(Project).where(Project.workspace_id == workspace_id, Project.id == project_id)
    project = (await db.execute(stmt)).scalars().first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    valid_states = ["IDEA", "PROTOTYPE", "VALIDATION", "MVP", "INCUBATION", "PILOT", "PRODUCTION", "ARCHIVED"]
    if new_state not in valid_states:
        raise HTTPException(status_code=400, detail=f"Invalid lifecycle state: {new_state}")

    # Generate a deterministic UUID for the state node so it's consistent across transitions
    state_id = uuid.uuid5(uuid.NAMESPACE_OID, f"LifecycleState:{new_state}")
    
    graph_service = KnowledgeGraphService(db)
    # Create the transition edge
    await graph_service.create_edge(
        workspace_id=workspace_id,
        source_type="Project",
        source_id=project_id,
        target_type="LifecycleState",
        target_id=state_id,
        relation_type="REACHED_STATE",
        properties={
            "state": new_state,
            "transitioned_at": datetime.utcnow().isoformat(),
            "actor_id": str(user.id),
            "actor_name": user.full_name,
            "notes": notes
        }
    )
    
    # Update the project's internal status field for quick indexing
    project.status = new_state.lower()
    await db.commit()
    await db.refresh(project)
    return project

async def get_project_transitions(db: AsyncSession, workspace_id: uuid.UUID, project_id: uuid.UUID):
    graph_service = KnowledgeGraphService(db)
    edges = await graph_service.get_edges(node_id=project_id, workspace_id=workspace_id, direction="out")
    
    transitions = []
    for edge in edges:
        if edge.relation_type == "REACHED_STATE" and edge.target_type == "LifecycleState":
            transitions.append(edge.properties)
            
    # Sort transitions by chronological order
    transitions.sort(key=lambda x: x.get("transitioned_at", ""))
    return transitions
