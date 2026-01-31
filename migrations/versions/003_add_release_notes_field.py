"""Add notes field to releases table.

Revision ID: 003
Revises: a9fd410f4ca5
Create Date: 2026-01-31

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003_add_release_notes_field'
down_revision = 'a9fd410f4ca5'
branch_labels = None
depends_on = None


def upgrade():
    """Add notes column to releases table."""
    op.add_column('releases', sa.Column('notes', sa.Text(), nullable=True))


def downgrade():
    """Remove notes column from releases table."""
    op.drop_column('releases', 'notes')
