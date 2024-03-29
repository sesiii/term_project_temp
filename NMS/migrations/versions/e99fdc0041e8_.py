"""empty message

Revision ID: e99fdc0041e8
Revises: c5b35a81fe77
Create Date: 2024-03-12 21:00:27.603864

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'e99fdc0041e8'
down_revision = 'c5b35a81fe77'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('student', schema=None) as batch_op:
        batch_op.drop_index('ix_student_name')
        batch_op.drop_index('student_id')

    op.drop_table('student')
    with op.batch_alter_table('donor', schema=None) as batch_op:
        batch_op.add_column(sa.Column('help_type', sa.String(length=64), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('donor', schema=None) as batch_op:
        batch_op.drop_column('help_type')

    op.create_table('student',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', mysql.VARCHAR(length=64), nullable=True),
    sa.Column('age', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('class_', mysql.VARCHAR(length=64), nullable=True),
    sa.Column('school', mysql.VARCHAR(length=128), nullable=True),
    sa.Column('parental_income', mysql.FLOAT(), nullable=True),
    sa.Column('help_type', mysql.VARCHAR(length=128), nullable=True),
    sa.Column('student_id', mysql.VARCHAR(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    with op.batch_alter_table('student', schema=None) as batch_op:
        batch_op.create_index('student_id', ['student_id'], unique=True)
        batch_op.create_index('ix_student_name', ['name'], unique=False)

    # ### end Alembic commands ###
