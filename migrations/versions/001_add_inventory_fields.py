"""Add inventory fields to releases table.

Revision ID: 001
Revises:
Create Date: 2026-01-30

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001_add_inventory_fields'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Add inventory-related columns to the releases table."""
    # Add inventory fields for seller mode
    op.add_column('releases', sa.Column('listing_id', sa.Integer(), nullable=True))
    op.add_column('releases', sa.Column('condition', sa.String(length=50), nullable=True))
    op.add_column('releases', sa.Column('sleeve_condition', sa.String(length=50), nullable=True))
    op.add_column('releases', sa.Column('price', sa.String(length=50), nullable=True))
    op.add_column('releases', sa.Column('location', sa.String(length=200), nullable=True))
    op.add_column('releases', sa.Column('inventory_synced_at', sa.DateTime(), nullable=True))

    # Add index on listing_id for faster lookups
    op.create_index(op.f('ix_releases_listing_id'), 'releases', ['listing_id'], unique=False)


def downgrade():
    """Remove inventory-related columns from the releases table."""
    op.drop_index(op.f('ix_releases_listing_id'), table_name='releases')
    op.drop_column('releases', 'inventory_synced_at')
    op.drop_column('releases', 'location')
    op.drop_column('releases', 'price')
    op.drop_column('releases', 'sleeve_condition')
    op.drop_column('releases', 'condition')
    op.drop_column('releases', 'listing_id')
