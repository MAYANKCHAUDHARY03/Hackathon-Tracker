"""Add portable_project_id to projects

Revision ID: d0cb9c9a7260
Revises: 11e264e5b395
Create Date: 2026-08-21 15:57:33.453906

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd0cb9c9a7260'
down_revision: Union[str, None] = '11e264e5b395'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.add_column(sa.Column('portable_project_id', sa.UUID(), nullable=True))
        batch_op.create_foreign_key('fk_projects_portable_project_id', 'portable_project_identities', ['portable_project_id'], ['id'], ondelete='SET NULL')
        batch_op.create_index('ix_projects_portable_project_id', ['portable_project_id'])

def downgrade() -> None:
    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.drop_index('ix_projects_portable_project_id')
        batch_op.drop_constraint('fk_projects_portable_project_id', type_='foreignkey')
        batch_op.drop_column('portable_project_id')
