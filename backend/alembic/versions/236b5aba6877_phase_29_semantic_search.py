"""phase 29 semantic search

Revision ID: 236b5aba6877
Revises: a12a328ebecd
Create Date: 2026-08-11 13:56:30.811874

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '236b5aba6877'
down_revision: Union[str, None] = 'a12a328ebecd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('content_embeddings',
    sa.Column('workspace_id', sa.UUID(), nullable=False),
    sa.Column('entity_type', sa.String(), nullable=False),
    sa.Column('entity_id', sa.UUID(), nullable=False),
    sa.Column('embedding', sa.JSON(), nullable=False),
    sa.Column('content_hash', sa.String(), nullable=False),
    sa.Column('model_version', sa.String(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_content_embeddings_entity_id'), 'content_embeddings', ['entity_id'], unique=False)
    op.create_index(op.f('ix_content_embeddings_entity_type'), 'content_embeddings', ['entity_type'], unique=False)
    op.create_index(op.f('ix_content_embeddings_workspace_id'), 'content_embeddings', ['workspace_id'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_content_embeddings_workspace_id'), table_name='content_embeddings')
    op.drop_index(op.f('ix_content_embeddings_entity_type'), table_name='content_embeddings')
    op.drop_index(op.f('ix_content_embeddings_entity_id'), table_name='content_embeddings')
    op.drop_table('content_embeddings')
