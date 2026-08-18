"""add_agent_memories_table

Revision ID: 75c2f25cf17a
Revises: cfc855786c5f
Create Date: 2026-08-18 15:45:08.941134

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '75c2f25cf17a'
down_revision: Union[str, None] = 'cfc855786c5f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'agent_memories',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('workspace_id', sa.UUID(), nullable=False),
        sa.Column('agent_name', sa.String(length=100), nullable=False),
        sa.Column('memory_type', sa.String(length=50), nullable=False),
        sa.Column('content', sa.JSON(), nullable=False),
        sa.Column('source_id', sa.String(length=255), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agent_memories_workspace_id'), 'agent_memories', ['workspace_id'], unique=False)
    op.create_index(op.f('ix_agent_memories_agent_name'), 'agent_memories', ['agent_name'], unique=False)
    op.create_index(op.f('ix_agent_memories_memory_type'), 'agent_memories', ['memory_type'], unique=False)
    op.create_index(op.f('ix_agent_memories_expires_at'), 'agent_memories', ['expires_at'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_agent_memories_expires_at'), table_name='agent_memories')
    op.drop_index(op.f('ix_agent_memories_memory_type'), table_name='agent_memories')
    op.drop_index(op.f('ix_agent_memories_agent_name'), table_name='agent_memories')
    op.drop_index(op.f('ix_agent_memories_workspace_id'), table_name='agent_memories')
    op.drop_table('agent_memories')
