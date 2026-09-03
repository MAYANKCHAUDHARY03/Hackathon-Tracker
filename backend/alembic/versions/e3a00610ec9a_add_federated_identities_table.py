"""add federated_identities table

Revision ID: e3a00610ec9a
Revises: d0cb9c9a7260
Create Date: 2026-08-21 16:04:40.701962

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e3a00610ec9a'
down_revision: Union[str, None] = 'd0cb9c9a7260'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('federated_identities',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('home_org_id', sa.UUID(), nullable=False),
    sa.Column('target_org_id', sa.UUID(), nullable=False),
    sa.Column('status', sa.Enum('ACTIVE', 'REVOKED', 'EXPIRED', name='federationstatus'), nullable=False),
    sa.Column('granted_scopes', sa.JSON(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.ForeignKeyConstraint(['home_org_id'], ['organizations.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['target_org_id'], ['organizations.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_fed_identity_link', 'federated_identities', ['user_id', 'home_org_id', 'target_org_id'], unique=True)
    op.create_index(op.f('ix_federated_identities_home_org_id'), 'federated_identities', ['home_org_id'], unique=False)
    op.create_index(op.f('ix_federated_identities_target_org_id'), 'federated_identities', ['target_org_id'], unique=False)
    op.create_index(op.f('ix_federated_identities_user_id'), 'federated_identities', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_federated_identities_user_id'), table_name='federated_identities')
    op.drop_index(op.f('ix_federated_identities_target_org_id'), table_name='federated_identities')
    op.drop_index(op.f('ix_federated_identities_home_org_id'), table_name='federated_identities')
    op.drop_index('ix_fed_identity_link', table_name='federated_identities')
    op.drop_table('federated_identities')
