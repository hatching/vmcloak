# Copyright (C) 2021 Hatching B.V.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

"""Add _installed column

Revision ID: d6c5bf858df1
Revises: f5b14c62e62c
Create Date: 2021-11-03 23:10:43.966405

"""

# Revision identifiers, used by Alembic.
revision = 'd6c5bf858df1'
down_revision = 'f5b14c62e62c'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('image', sa.Column('_installed', sa.Text(), nullable=True))

def downgrade():
    pass