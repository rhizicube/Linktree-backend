"""Including profilepicture for profile

Revision ID: 873152f43a75
Revises: 66f6cd89bba6
Create Date: 2022-12-28 22:46:17.730562

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '873152f43a75'
down_revision = '66f6cd89bba6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_picture')
    op.drop_constraint('profile_picture_profile_image_id_fkey', 'profile_picture', type_='foreignkey')
    op.create_foreign_key(None, 'profile_picture', 'profile', ['profile_image_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'profile_picture', type_='foreignkey')
    op.create_foreign_key('profile_picture_profile_image_id_fkey', 'profile_picture', 'user', ['profile_image_id'], ['username'])
    op.create_table('user_picture',
    sa.Column('width', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('height', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('mimetype', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('original', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('profile_image_id', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['profile_image_id'], ['user.username'], name='user_picture_profile_image_id_fkey'),
    sa.PrimaryKeyConstraint('width', 'height', 'profile_image_id', name='user_picture_pkey')
    )
    # ### end Alembic commands ###
