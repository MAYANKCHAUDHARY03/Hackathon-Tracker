"""Add integration models

Revision ID: ee86acbe1e02
Revises: e661fa01abdb
Create Date: 2026-08-07 14:03:19.336540

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ee86acbe1e02'
down_revision: Union[str, None] = 'e661fa01abdb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('external_submission_connections',
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('provider_name', sa.String(length=50), nullable=False),
    sa.Column('credentials', sa.JSON(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('last_sync_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('external_submission_mappings',
    sa.Column('submission_id', sa.UUID(), nullable=False),
    sa.Column('connection_id', sa.UUID(), nullable=False),
    sa.Column('external_reference_id', sa.String(length=255), nullable=False),
    sa.Column('external_status', sa.String(length=50), nullable=True),
    sa.Column('sync_metadata', sa.JSON(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['connection_id'], ['external_submission_connections.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['submission_id'], ['round_submissions.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('external_submission_mappings')
    op.drop_table('external_submission_connections')
