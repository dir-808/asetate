"""Add inventory fields and InventoryListing table.

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
    """Add inventory-related columns and tables."""
    # Add inventory fields to releases table (for backwards compatibility)
    op.add_column('releases', sa.Column('listing_id', sa.Integer(), nullable=True))
    op.add_column('releases', sa.Column('condition', sa.String(length=50), nullable=True))
    op.add_column('releases', sa.Column('sleeve_condition', sa.String(length=50), nullable=True))
    op.add_column('releases', sa.Column('price', sa.String(length=50), nullable=True))
    op.add_column('releases', sa.Column('location', sa.String(length=200), nullable=True))
    op.add_column('releases', sa.Column('inventory_synced_at', sa.DateTime(), nullable=True))
    op.add_column('releases', sa.Column('last_exported_at', sa.DateTime(), nullable=True))

    # Add index on listing_id for faster lookups
    op.create_index(op.f('ix_releases_listing_id'), 'releases', ['listing_id'], unique=False)

    # Create inventory_listings table (supports multiple listings per release)
    op.create_table(
        'inventory_listings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('release_id', sa.Integer(), nullable=True),
        sa.Column('listing_id', sa.Integer(), nullable=False),
        sa.Column('discogs_release_id', sa.Integer(), nullable=False),
        sa.Column('release_title', sa.String(length=500), nullable=True),
        sa.Column('release_artist', sa.String(length=500), nullable=True),
        sa.Column('condition', sa.String(length=50), nullable=True),
        sa.Column('sleeve_condition', sa.String(length=50), nullable=True),
        sa.Column('price', sa.String(length=50), nullable=True),
        sa.Column('original_price', sa.String(length=50), nullable=True),
        sa.Column('location', sa.String(length=200), nullable=True),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='for_sale'),
        sa.Column('listed_at', sa.DateTime(), nullable=True),
        sa.Column('sold_at', sa.DateTime(), nullable=True),
        sa.Column('removed_at', sa.DateTime(), nullable=True),
        sa.Column('synced_at', sa.DateTime(), nullable=True),
        sa.Column('last_exported_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('notification_dismissed', sa.Boolean(), nullable=True, server_default='0'),
        sa.ForeignKeyConstraint(['release_id'], ['releases.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'listing_id', name='unique_listing_per_user'),
    )
    op.create_index(op.f('ix_inventory_listings_discogs_release_id'), 'inventory_listings', ['discogs_release_id'], unique=False)
    op.create_index(op.f('ix_inventory_listings_listing_id'), 'inventory_listings', ['listing_id'], unique=False)
    op.create_index(op.f('ix_inventory_listings_release_id'), 'inventory_listings', ['release_id'], unique=False)
    op.create_index(op.f('ix_inventory_listings_user_id'), 'inventory_listings', ['user_id'], unique=False)


def downgrade():
    """Remove inventory-related columns and tables."""
    # Drop inventory_listings table
    op.drop_index(op.f('ix_inventory_listings_user_id'), table_name='inventory_listings')
    op.drop_index(op.f('ix_inventory_listings_release_id'), table_name='inventory_listings')
    op.drop_index(op.f('ix_inventory_listings_listing_id'), table_name='inventory_listings')
    op.drop_index(op.f('ix_inventory_listings_discogs_release_id'), table_name='inventory_listings')
    op.drop_table('inventory_listings')

    # Remove inventory columns from releases
    op.drop_index(op.f('ix_releases_listing_id'), table_name='releases')
    op.drop_column('releases', 'last_exported_at')
    op.drop_column('releases', 'inventory_synced_at')
    op.drop_column('releases', 'location')
    op.drop_column('releases', 'price')
    op.drop_column('releases', 'sleeve_condition')
    op.drop_column('releases', 'condition')
    op.drop_column('releases', 'listing_id')
