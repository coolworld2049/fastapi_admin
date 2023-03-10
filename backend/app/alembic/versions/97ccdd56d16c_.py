"""empty message

Revision ID: 97ccdd56d16c
Revises: 
Create Date: 2023-02-12 19:25:28.438845

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '97ccdd56d16c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.BIGINT(), autoincrement=True, nullable=False),
    sa.Column('email', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('hashed_password', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('role', postgresql.ENUM('admin', 'user', name='user_role'), server_default=sa.text("'user'::user_role"), autoincrement=False, nullable=False),
    sa.Column('full_name', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('username', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('age', sa.SMALLINT(), autoincrement=False, nullable=True),
    sa.Column('phone', sa.VARCHAR(length=20), autoincrement=False, nullable=True),
    sa.Column('avatar', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('is_active', sa.BOOLEAN(), server_default=sa.text('true'), autoincrement=False, nullable=False),
    sa.Column('is_superuser', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.CheckConstraint('full_name <> role::text', name='full_name != role'),
    sa.CheckConstraint('username <> role::text', name='username != role'),
    sa.PrimaryKeyConstraint('id', name='user_pkey'),
    sa.UniqueConstraint('email', name='user_email_key'),
    sa.UniqueConstraint('username', name='user_username_key')
    )
    # ### end Alembic commands ###
