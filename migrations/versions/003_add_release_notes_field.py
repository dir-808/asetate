"""Add notes field to releases table.

Revision ID: 003
Revises: 002_add_sync_progress_current_release
Create Date: 2026-01-31

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003_add_release_notes_field'
down_revision = '002_add_sync_progress_current_release'
branch_labels = None
depends_on = None


def upgrade():
    """Add notes column to releases table."""
    op.add_column('releases', sa.Column('notes', sa.Text(), nullable=True))


def downgrade():
    """Remove notes column from releases table."""
    op.drop_column('releases', 'notes')
