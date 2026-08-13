"""Add agent_approval_requests table

Revision ID: cfc855786c5f
Revises: 2d0e3813642c
Create Date: 2026-08-13 12:26:42.722182

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cfc855786c5f'
down_revision: Union[str, None] = '2d0e3813642c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('agent_approval_requests',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('agent_name', sa.String(), nullable=False),
    sa.Column('tool_name', sa.String(), nullable=False),
    sa.Column('parameters_json', sa.JSON(), nullable=False),
    sa.Column('risk_level', sa.String(), nullable=False),
    sa.Column('status', sa.Enum('PENDING', 'APPROVED', 'REJECTED', name='approvalstatus'), nullable=False),
    sa.Column('justification', sa.String(), nullable=True),
    sa.Column('requested_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('resolved_by_id', sa.UUID(), nullable=True),
    sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['resolved_by_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('agent_approval_requests', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_agent_approval_requests_workspace_id'), ['workspace_id'], unique=False)

def downgrade() -> None:
    with op.batch_alter_table('agent_approval_requests', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_agent_approval_requests_workspace_id'))
    op.drop_table('agent_approval_requests')
