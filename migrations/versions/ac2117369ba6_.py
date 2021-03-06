"""empty message

Revision ID: ac2117369ba6
Revises: ea29ab8b3610
Create Date: 2020-07-07 23:22:36.901256

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ac2117369ba6'
down_revision = 'ea29ab8b3610'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'show', 'venue', ['venue_id'], ['id'])
    op.create_foreign_key(None, 'show', 'artist', ['artist_id'], ['id'])
    op.drop_column('show', 'venue_name')
    op.drop_column('show', 'start_time')
    op.drop_column('show', 'artist_image_link')
    op.drop_column('show', 'id')
    op.drop_column('show', 'artist_name')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('show', sa.Column('artist_name', sa.VARCHAR(length=200), autoincrement=False, nullable=True))
    op.add_column('show', sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False))
    op.add_column('show', sa.Column('artist_image_link', sa.VARCHAR(length=500), autoincrement=False, nullable=True))
    op.add_column('show', sa.Column('start_time', sa.VARCHAR(length=200), autoincrement=False, nullable=True))
    op.add_column('show', sa.Column('venue_name', sa.VARCHAR(length=200), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'show', type_='foreignkey')
    op.drop_constraint(None, 'show', type_='foreignkey')
    # ### end Alembic commands ###
