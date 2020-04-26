"""empty message

Revision ID: a57e5a8ec338
Revises: ae7d4dde43f3
Create Date: 2020-02-29 20:25:34.497419

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a57e5a8ec338'
down_revision = 'ae7d4dde43f3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Show', 'start_time',
               existing_type=sa.VARCHAR(),
               type_=sa.DateTime(),
               existing_nullable=True,
               postgresql_using='start_time::timestamp without time zone')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Show', 'start_time',
               existing_type=sa.DateTime(),
               type_=sa.VARCHAR(),
               existing_nullable=True)
    # ### end Alembic commands ###
