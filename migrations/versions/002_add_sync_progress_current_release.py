"""Add current release tracking fields to sync_progress.

Revision ID: 002
Revises: 001_add_inventory_fields
Create Date: 2026-01-31

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002_add_sync_progress_current_release'
down_revision = '001_add_inventory_fields'
branch_labels = None
depends_on = None


def upgrade():
    """Add current release tracking columns to sync_progress."""
    op.add_column('sync_progress', sa.Column('current_release_artist', sa.String(length=500), nullable=True))
    op.add_column('sync_progress', sa.Column('current_release_title', sa.String(length=500), nullable=True))


def downgrade():
    """Remove current release tracking columns from sync_progress."""
    op.drop_column('sync_progress', 'current_release_title')
    op.drop_column('sync_progress', 'current_release_artist')
