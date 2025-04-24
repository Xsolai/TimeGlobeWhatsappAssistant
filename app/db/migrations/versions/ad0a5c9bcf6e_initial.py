"""initial

Revision ID: ad0a5c9bcf6e
Revises: 
Create Date: 2024-04-11 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite


# revision identifiers, used by Alembic.
revision = 'ad0a5c9bcf6e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create businesses table with all fields
    op.create_table('businesses',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('business_name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password', sa.String(), nullable=False),
        sa.Column('phone_number', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        
        # Twilio fields
        sa.Column('twilio_subaccount_sid', sa.String(), nullable=True),
        sa.Column('twilio_auth_token', sa.String(), nullable=True),
        sa.Column('whatsapp_number', sa.String(), nullable=True),
        sa.Column('waba_status', sa.String(), nullable=True),
        
        # WhatsApp Sender fields
        sa.Column('whatsapp_sender_sid', sa.String(), nullable=True),
        sa.Column('whatsapp_sender_id', sa.String(), nullable=True),
        sa.Column('waba_id', sa.String(), nullable=True),
        sa.Column('whatsapp_status', sa.String(), nullable=True),
        sa.Column('whatsapp_profile', sqlite.JSON(), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    # Add new WhatsApp-related columns to businesses table
    with op.batch_alter_table('businesses') as batch_op:
        batch_op.add_column(sa.Column('whatsapp_sender_sid', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('whatsapp_sender_id', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('waba_id', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('whatsapp_status', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('whatsapp_profile', sqlite.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_table('businesses')

    # Remove the added columns
    with op.batch_alter_table('businesses') as batch_op:
        batch_op.drop_column('whatsapp_sender_sid')
        batch_op.drop_column('whatsapp_sender_id')
        batch_op.drop_column('waba_id')
        batch_op.drop_column('whatsapp_status')
        batch_op.drop_column('whatsapp_profile') 