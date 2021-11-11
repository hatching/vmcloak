# Copyright (C) 2021 Hatching B.V.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

"""Add mac column to image and snapshot

Revision ID: f5b14c62e62c
Revises: 5a5957711538
Create Date: 2021-11-03 15:12:45.181910

"""

# Revision identifiers, used by Alembic.
revision = 'f5b14c62e62c'
down_revision = '5a5957711538'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('image', sa.Column('mac', sa.String(length=32), nullable=True))
    op.add_column('snapshot', sa.Column('mac', sa.String(length=32), nullable=True))

def downgrade():
    pass
