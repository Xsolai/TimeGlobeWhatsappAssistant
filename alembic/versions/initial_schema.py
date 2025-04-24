"""Initial schema

Revision ID: initial
Revises: 
Create Date: 2024-04-11 08:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create businesses table
    op.create_table(
        'businesses',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('business_name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password', sa.String(), nullable=False),
        sa.Column('phone_number', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('twilio_subaccount_sid', sa.String(), nullable=True),
        sa.Column('twilio_auth_token', sa.String(), nullable=True),
        sa.Column('whatsapp_number', sa.String(), nullable=True),
        sa.Column('waba_status', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    # Create subscription_plans table
    op.create_table(
        'subscription_plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('duration_days', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create business_subscriptions table
    op.create_table(
        'business_subscriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('business_id', sa.String(), nullable=False),
        sa.Column('subscription_plan_id', sa.Integer(), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id']),
        sa.ForeignKeyConstraint(['subscription_plan_id'], ['subscription_plans.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Create WhatsAppSenders table
    op.create_table(
        'WhatsAppSenders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sender_id', sa.String(), nullable=True),
        sa.Column('phone_number', sa.String(), nullable=True),
        sa.Column('business_name', sa.String(), nullable=True),
        sa.Column('about', sa.String(), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('address', sa.String(), nullable=True),
        sa.Column('business_type', sa.String(), nullable=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('website', sa.String(), nullable=True),
        sa.Column('logo_url', sa.String(), nullable=True),
        sa.Column('business_id', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('sender_id'),
        sa.UniqueConstraint('phone_number')
    )


def downgrade() -> None:
    op.drop_table('WhatsAppSenders')
    op.drop_table('business_subscriptions')
    op.drop_table('subscription_plans')
    op.drop_table('businesses') 