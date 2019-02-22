# Copyright (C) 2018-2019 Hatching B.V.
# This file is part of VMCloak - http://www.vmcloak.org/.
# See the file 'docs/LICENSE.txt' for copying permission.

"""Add paravirtprovider column

Revision ID: 5a5957711538
Revises: 34c908159434
Create Date: 2018-10-08 17:22:15.370000

"""

# Revision identifiers, used by Alembic.
revision = "5a5957711538"
down_revision = "34c908159434"

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(
        "image", sa.Column("paravirtprovider", sa.String(32), default="default")
    )

def downgrade():
    pass
