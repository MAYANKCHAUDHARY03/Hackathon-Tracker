"""Add repository audits

Revision ID: 33015e870c8d
Revises: 75c2f25cf17a
Create Date: 2026-08-18 15:56:57.889382

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '33015e870c8d'
down_revision: Union[str, None] = '75c2f25cf17a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('repository_audits',
    sa.Column('project_id', sa.UUID(), nullable=False),
    sa.Column('cyclomatic_complexity_score', sa.Float(), nullable=True),
    sa.Column('sast_vulnerabilities_count', sa.Integer(), nullable=True),
    sa.Column('guideline_adherence_score', sa.Float(), nullable=True),
    sa.Column('sast_findings', sa.JSON(), nullable=True),
    sa.Column('guideline_violations', sa.JSON(), nullable=True),
    sa.Column('audited_by_agent_id', sa.String(), nullable=True),
    sa.Column('status', sa.String(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('repository_audits')
