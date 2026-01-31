"""Add additional metadata fields to releases table.

Revision ID: 004
Revises: 003_add_release_notes_field
Create Date: 2026-01-31

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '004_add_release_metadata_fields'
down_revision = '003_add_release_notes_field'
branch_labels = None
depends_on = None


def upgrade():
    """Add country, format_details, genres, and styles columns to releases table."""
    op.add_column('releases', sa.Column('country', sa.String(100), nullable=True))
    op.add_column('releases', sa.Column('format_details', sa.String(500), nullable=True))
    op.add_column('releases', sa.Column('genres', sa.JSON(), nullable=True))
    op.add_column('releases', sa.Column('styles', sa.JSON(), nullable=True))


def downgrade():
    """Remove metadata columns from releases table."""
    op.drop_column('releases', 'styles')
    op.drop_column('releases', 'genres')
    op.drop_column('releases', 'format_details')
    op.drop_column('releases', 'country')
