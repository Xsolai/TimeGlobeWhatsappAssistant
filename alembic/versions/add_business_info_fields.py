"""add business info fields

Revision ID: 2025_05_05_23_50
Revises: initial_schema
Create Date: 2025-05-05 23:50:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2025_05_05_23_50'
down_revision = 'initial_schema'
branch_labels = None
depends_on = None


def upgrade():
    # Add new business information fields to the businesses table
    op.add_column('businesses', sa.Column('tax_id', sa.String(), nullable=True))
    op.add_column('businesses', sa.Column('street_address', sa.String(), nullable=True))
    op.add_column('businesses', sa.Column('postal_code', sa.String(), nullable=True))
    op.add_column('businesses', sa.Column('city', sa.String(), nullable=True))
    op.add_column('businesses', sa.Column('country', sa.String(), nullable=True))
    op.add_column('businesses', sa.Column('contact_person', sa.String(), nullable=True))


def downgrade():
    # Drop the new columns in case of downgrade
    op.drop_column('businesses', 'tax_id')
    op.drop_column('businesses', 'street_address')
    op.drop_column('businesses', 'postal_code')
    op.drop_column('businesses', 'city')
    op.drop_column('businesses', 'country')
    op.drop_column('businesses', 'contact_person') 