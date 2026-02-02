"""Add catalogue number field to releases table.

Revision ID: 005
Revises: 004_add_release_metadata_fields
Create Date: 2026-02-02

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '005_add_catno_field'
down_revision = '004_add_release_metadata_fields'
branch_labels = None
depends_on = None


def upgrade():
    """Add catno column to releases table."""
    op.add_column('releases', sa.Column('catno', sa.String(100), nullable=True))


def downgrade():
    """Remove catno column from releases table."""
    op.drop_column('releases', 'catno')
