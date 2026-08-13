"""Add secret fields to products and receipt tracking to orders

Revision ID: 0003_secret_product_fields
Revises: 9e2265d6359b
Create Date: 2026-08-14 01:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0003_secret_product_fields'
down_revision: Union[str, None] = '9e2265d6359b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add public and secret content fields to products
    op.add_column('products', sa.Column('public_description', sa.TEXT(), nullable=True))
    op.add_column('products', sa.Column('public_image_url', sa.TEXT(), nullable=True))
    op.add_column('products', sa.Column('secret_description', sa.TEXT(), nullable=True))
    op.add_column('products', sa.Column('secret_image_url', sa.TEXT(), nullable=True))

    # Add receipt tracking fields to orders
    op.add_column('orders', sa.Column('receipt_confirmed', sa.BOOLEAN(), nullable=False, server_default='false'))
    op.add_column('orders', sa.Column('receipt_issue_reported', sa.BOOLEAN(), nullable=False, server_default='false'))


def downgrade() -> None:
    op.drop_column('orders', 'receipt_issue_reported')
    op.drop_column('orders', 'receipt_confirmed')
    op.drop_column('products', 'secret_image_url')
    op.drop_column('products', 'secret_description')
    op.drop_column('products', 'public_image_url')
    op.drop_column('products', 'public_description')
