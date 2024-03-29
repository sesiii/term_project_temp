"""Initial migration.

Revision ID: 0340f6ef3de0
Revises: 
Create Date: 2024-03-10 10:59:16.535568

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0340f6ef3de0'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('student',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('age', sa.Integer(), nullable=True),
    sa.Column('class_', sa.String(length=64), nullable=True),
    sa.Column('school', sa.String(length=128), nullable=True),
    sa.Column('parental_income', sa.Float(), nullable=True),
    sa.Column('help_type', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('student', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_student_name'), ['name'], unique=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('student', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_student_name'))

    op.drop_table('student')
    # ### end Alembic commands ###
